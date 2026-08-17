from app.schemas.user import UserCreate, UserLogin
from app.schemas.email import EmailCodeConfirm
from sqlalchemy.orm import Session
from app.models.user import User
from fastapi import Response
from email.message import EmailMessage
from datetime import datetime, timezone
from app.repository.user_repository import get_user_by_email, create_user
from app.repository.email_repository import (
    create_temp_email, 
    get_email_by_user, 
    delete_temporary_email
)
from app.repository.password_recovery_repository import (
    add_password_recovery,
    delete_all_password_recovery
)
from app.repository.recovery_code_repository import (
    create_many_recovery_code,
    set_many_recovery_code,
    validate_recovery_code
)
from app.core.config import settings
from app.core.exceptions import (
    UserAlreadyExistsError,
    InvalidEmailOrPasswordError,
    EmailConfirmationRequiredError,
    TwoFactorAuthAlreadyConfiguredError,
    InvalidTwoFactorAuthCodeError,
    EmailAlreadyConfirmedError, 
    InvalidEmailConfirmationCodeError,
    ExpiredEmailConfirmationCodeError,
    UserNotFoundError
)
from app.core.security import (
    password_hash, 
    setup_2fa, 
    validate_2fa,
    configure_email,
    decrypt_message,
    generate_temporary_email,
    qrcode_generate_uri,
    create_token_jwt,
    delete_all_jwt_token,
    set_token,
    generate_recovery_codes,
    generate_strong_token,
    generate_hash_sha256
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

    delete_all_jwt_token(response)

    token = create_token_jwt(existing_user, settings.TEMPORARY_TOKEN_EXPIRE_MINUTES, "temporary")

    set_token(
        response,
        "temporary_token",
        token,
        "/Autenticar",
        settings.TEMPORARY_TOKEN_EXPIRE_MINUTES * 60,
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
    result = {}

    if not user.email_active:
        raise EmailConfirmationRequiredError()
    
    if not validate_2fa(user, otp):
        if not user.security_2fa_active or not validate_recovery_code(otp, user.id, session):
            raise InvalidTwoFactorAuthCodeError()

    if not user.security_2fa_active:
        codes = generate_recovery_codes()
        recovery_codes = create_many_recovery_code(codes, user.id)
        set_many_recovery_code(recovery_codes, session)

        user.security_2fa_active = True
        result["codigos"] = codes

    session.commit()

    delete_all_jwt_token(response)

    access_token = create_token_jwt(user, settings.ACCESS_TOKEN_EXPIRE_MINUTES, "access")
    refresh_token = create_token_jwt(user, settings.REFRESH_TOKEN_EXPIRE_MINUTES, "refresh")

    set_token(
        response,
        "access_token",
        access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    set_token(
        response,
        "refresh_token",
        refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )

    result["usuario"] = user
    return result

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

    if existing_temp_email.exp < datetime.now(timezone.utc):
        raise ExpiredEmailConfirmationCodeError()

    user.email_active = True
    if delete_temporary_email(user.email, session):
        print("ok")
    session.commit()
    session.refresh(user)
    return {"mensagem": "Email confirmado."}

def password_recovery_service(email: str, response: Response, session: Session):
    user = get_user_by_email(email, session)
    if not user:
        raise UserNotFoundError()

    token = generate_strong_token(32)
    token_hash = generate_hash_sha256(token)

    delete_all_password_recovery(email, session)
    add_password_recovery(email, token_hash, session)

    link = f"http://127.0.0.1:8000/ReporSenha?email={email}&token={token}"

    content = f"""
        <p>Olá,</p>
        <p>Acesse o <a href="{link}">Fast API repor senha</a> clicando no link.</p>
        """

    config, message = create_generic_email(email, content)
    send_email_service(config, message)

def create_generic_email(to: str, content: str):
    config = configure_email()
    message = EmailMessage()

    message["From"] = config["username"]
    message["To"] = to
    message["Subject"] = "FastAPI | Código de confirmação | 5 Minutos"
    message.set_content(content)

    return config, message