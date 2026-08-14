from pwdlib import PasswordHash
from app.models.user import User
from app.models.email import TemporaryEmailCode
from datetime import datetime, timezone, timedelta
from secrets import randbelow
from app.core.exceptions import (
    TwoFactorAuthNotConfiguredError,
    InvalidTwoFactorAuthCodeError
)
from fastapi.responses import StreamingResponse
from app.core.config import settings
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

import jwt
import pyotp
import base64
import qrcode
import io

password_hash = PasswordHash.recommended()

def setup_2fa(user: User) -> str:
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(
        name=user.email,
        issuer_name="FastAPI Security"
    )

    secret = encrypt_message(secret)

    return uri, secret

def validate_2fa(user: User, otp: str):
    ecrypted_secret = user.secret_key_2fa
    if not ecrypted_secret:
        raise TwoFactorAuthNotConfiguredError()
    
    decrypted_secret = decrypt_message(secret=ecrypted_secret)
    totp = pyotp.TOTP(decrypted_secret)

    if not totp.verify(otp=otp):
        raise InvalidTwoFactorAuthCodeError()

    return True

def qrcode_generate_uri(uri: str):
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )

    qr.add_data(uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")

def encrypt_message(secret: str):
    new_secret_key = format_secret_2fa()
    fernet = Fernet(new_secret_key)
    encrypted = fernet.encrypt(secret.encode())

    return encrypted.decode()

def decrypt_message(secret: str):
    new_secret_key = format_secret_2fa()
    fernet = Fernet(new_secret_key)
    decryped = fernet.decrypt(secret)

    return decryped.decode()

def format_secret_2fa() -> bytes:
    new_secret = settings.SECRET_KEY_2FA.encode('utf-8')
    salt = settings.SALT.encode()
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    
    new_secret = base64.urlsafe_b64encode(kdf.derive(new_secret))
    
    return new_secret

def create_token_jwt(user: User, minutes: int, type: str) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user.id),
        "iat": now,
        "type": type,
        "exp": now + timedelta(minutes=minutes),
    }

    token = jwt.encode(
        payload=payload,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token

def decode_token_jwt(token: str) -> dict:
    return jwt.decode(
        jwt=token,
        key=settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        options={
            "require": ["sub", "exp", "type"]
        }
    )

def configure_email() -> dict[str, str | None]:
    config = {
        "hostname": settings.SMTP_HOST,
        "port": settings.SMTP_PORT,
        "username": settings.SMTP_FROM,
        "password": settings.SMTP_PASSWORD,
    }

    return config

def generate_temporary_email(user: User) -> TemporaryEmailCode:
    info = TemporaryEmailCode()
    info.user_email = user.email
    code = f"{randbelow(1000000):06d}"

    info.temporary_code = encrypt_message(code)

    return info, code
