from app.schemas.user import UserCreate, UserLogin
from app.schemas.email import EmailCodeConfirm
from sqlalchemy.orm import Session
from app.models.user import User
from fastapi import Response
from email.message import EmailMessage
from datetime import datetime
from app.repository.user_repository import get_user_by_email, create_user
from app.repository.email_repository import create_temp_email, get_email_by_user
from app.core.exceptions import (
    UserAlreadyExistsError,
    InvalidEmailOrPasswordError,
    EmailConfirmationRequiredError,
    TwoFactorAuthAlreadyConfiguredError,
    InvalidTwoFactorAuthCodeError,
    EmailAlreadyConfirmedError, 
    InvalidEmailConfirmationCodeError,
    ExpiredEmailConfirmationCodeError
)
from app.core.security import (
    password_hash, 
    setup_2fa, 
    validate_2fa,
    configure_email,
    decrypt_message,
    generate_temporary_email,
    qrcode_generate_uri,
    create_token_jwt
)

import aiosmtplib

def create_account_service(user: UserCreate, session: Session) -> bool:
    with session.begin():
        existing_user = get_user_by_email(user.email, session)

        if existing_user:
            raise UserAlreadyExistsError()

        new_user = User(
            name=user.name,
            email=user.email,
            password=password_hash.hash(user.password)
        )

        create_user(new_user, session)

    session.refresh(new_user)
    return {"mensagem": "Conta criada com sucesso."}

def login_service(user: UserLogin, session: Session, response: Response) -> User | None:
    existing_user = get_user_by_email(user.email, session)
    if not existing_user or (not password_hash.verify(user.password, existing_user.password)):
        raise InvalidEmailOrPasswordError()     

    token = create_token_jwt(existing_user, 5, "temporary")

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
        raise EmailConfirmationRequiredError()
    
    if not validate_2fa(user, otp):
        raise InvalidTwoFactorAuthCodeError()

    if not user.security_2fa_active:
        user.security_2fa_active = True
        session.commit()

    token = create_token_jwt(user, 15, "access")

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
    user.secret_key_2fa = secret
    session.commit()

    return qrcode_generate_uri(uri=uri)

def active_security_2fa_service(user: User, session: Session):
    if not user.email_active:
        raise EmailConfirmationRequiredError()
    
    if user.security_2fa_active:
        raise TwoFactorAuthAlreadyConfiguredError()
    
    return create_2fa(user, session)

def creat_email(user: User, session: Session):
    if user.email_active:
            raise EmailAlreadyConfirmedError()
        
    config = configure_email()
    message = EmailMessage()
    temporary_email, code = generate_temporary_email(user)

    create_temp_email(temporary_email, session)
    session.refresh(temporary_email)
    
    message["From"] = config["username"]
    message["To"] = user.email
    message["Subject"] = "FastAPI | Código de confirmação | 5 Minutos"
    message.set_content(code)

    return config, message

    
async def send_email_service(config, message):
    config = configure_email()
    
    await aiosmtplib.send(
        message,
        hostname=config["hostname"],
        port=config["port"],
        username=config["username"],
        password=config["password"],
        start_tls=True,
        validate_certs=False
    )

async def confirm_email_service(user: User, session: Session, code: EmailCodeConfirm):
    if user.email_active:
        raise EmailAlreadyConfirmedError()
    
    existing_temp_email = get_email_by_user(user.email, session)
    if not existing_temp_email:
        await send_email_service(user, session)
        return {"message": "Email colocado para envio."}
    
    existing_code = decrypt_message(existing_temp_email.temporary_code)

    if existing_code != code.temporary_code:
        raise InvalidEmailConfirmationCodeError()

    if existing_temp_email.exp < datetime.now():
        raise ExpiredEmailConfirmationCodeError()

    user.email_active = True
    session.commit()
    session.refresh(user)
    return {"mensagem": "Email confirmado."}
