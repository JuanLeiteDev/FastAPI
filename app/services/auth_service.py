from app.schemas.user import UserCreate, UserLogin
from app.schemas.email import EmailConfirm
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.email import TemporaryEmail
from fastapi import HTTPException, Response
from email.message import EmailMessage
from secrets import randbelow
from datetime import datetime, timezone
from app.repository.user_repository import get_user_by_email, create_user
from app.repository.email_repository import create_email_repository, get_email_by_email
from app.security import (
    password_hash, 
    setup_2fa, 
    encrypt_message, 
    qrcode_generate, 
    create_token, 
    validate_2fa,
    configure_email,
    decrypt_message
)

import aiosmtplib

def create_account_service(user: UserCreate, session: Session) -> User:
    with session.begin():
        existing_user = get_user_by_email(user.email, session)

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Já existe um utilizador com este email."
            )

        new_user = User(
            name=user.name,
            email=user.email,
            password=password_hash.hash(user.password)
        )

        create_user(new_user, session)

    session.refresh(new_user)
    return new_user

def login_service(user: UserLogin, session: Session, response: Response) -> User | None:
    existing_user = get_user_by_email(user.email, session)
    if not existing_user or (not password_hash.verify(user.password, existing_user.password)):
        raise HTTPException(
            status_code=401,
            detail="Email ou senha incorretos."
        )      

    token = create_token(existing_user, 5, "temporary")

    response.set_cookie(
        key="temporary_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=900,
        path="/Autenticar"
    )

    if not existing_user.email_active:
        mensagem = "Necessário confirmar email."
    else:
        mensagem = "Autenticação 2FA obrigatória."
        
    return {
        "mensagem": mensagem,
        "email": existing_user.email_active,
        "auth2fa": existing_user.security_2fa_active
    }

def confirm_2fa_service(otp: str, response: Response, user: User, session: Session):
    if not user.email_active:
        raise HTTPException(
            status_code=401,
            detail="É obrigatório a confirmação do e-mail primeiro."
        )
    
    if not validate_2fa(user, otp):
        raise HTTPException(
            status_code=401,
            detail="Código inválido"
        )

    if not user.security_2fa_active:
        user.security_2fa_active = True
        session.commit()

    token = create_token(user, 15, "access")

    response.delete_cookie(
        key="temporary_token",
        path="/Autenticar"
    )
    
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=900,
        path="/"
    )

    return user

def create_2fa(user: User, session: Session):
    uri, secret = setup_2fa(user)

    secret = encrypt_message(secret=secret)
    user.secret_key_2fa = secret
    session.commit()

    return qrcode_generate(uri=uri)

def active_security_2fa_service(user: User, session: Session):
    if not user.email_active:
        raise HTTPException(
            status_code=401,
            detail="É obrigatório a confirmação do e-mail primeiro."
        )
    
    if user.security_2fa_active:
        raise HTTPException(
            status_code=400,
            detail="Autenticação 2FA já foi configurada."
        )
    
    return create_2fa(user, session)

async def send_email_service(user: User, session: Session):
    config = configure_email()
    message = EmailMessage()
    code = f"{randbelow(1000000):06d}"

    temporary_email = TemporaryEmail()

    temporary_email.user_email = user.email
    temporary_email.temporary_code = encrypt_message(code)

    create_email_repository(temporary_email, session)
    session.refresh(temporary_email)
    
    message["From"] = config["username"]
    message["To"] = user.email
    message["Subject"] = "FastAPI | Código de confirmação | 5 Minutos"
    message.set_content(code)

    await aiosmtplib.send(
        message,
        hostname=config["hostname"],
        port=config["port"],
        username=config["username"],
        password=config["password"],
        start_tls=True
    )

def confirm_email_service(user: User, session: Session, code: EmailConfirm):
    existing_temp_email = get_email_by_email(user.email, session)
    existing_code = decrypt_message(existing_temp_email.temporary_code)

    if existing_code != code.code:
        raise HTTPException(
            status_code=400,
            detail="Código inválido."
        )

    if existing_temp_email.exp < datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Código expirado."
        )

    user.email_active = True
    session.commit()
    session.refresh(user)
    return user
