from pwdlib import PasswordHash
from app.models import User
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, Response
from fastapi.responses import StreamingResponse
from app.config import SECRET_KEY, SECRET_KEY_2FA, ALGORITHM, SALT
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from datetime import datetime

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

    return uri, secret

def validate_2fa(user: User, otp: str):
    ecrypted_secret = user.secret_key_2fa
    decrypted_secret = decrypt_secret_2fa(secret=ecrypted_secret)
    totp = pyotp.TOTP(decrypted_secret)

    if not totp.verify(otp=otp):
        return False

    return True

def qrcode_generate(uri: str):
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

def encrypt_secret_2fa(secret: str):
    new_secret_key = format_secret_2fa()
    fernet = Fernet(new_secret_key)
    encrypted = fernet.encrypt(secret.encode())

    return encrypted.decode()

def decrypt_secret_2fa(secret: str):
    new_secret_key = format_secret_2fa()
    fernet = Fernet(new_secret_key)
    decryped = fernet.decrypt(secret)

    return decryped.decode()

def format_secret_2fa() -> bytes:
    new_secret = SECRET_KEY_2FA.encode('utf-8')
    salt = SALT.encode()
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    
    new_secret = base64.urlsafe_b64encode(kdf.derive(new_secret))
    
    return new_secret

def create_token(user: User, minutes: int, type: str) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user.id),
        "iat": now,
        "type": type,
        "exp": now + timedelta(minutes=minutes),
    }

    token = jwt.encode(
        payload=payload,
        key=SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            jwt=token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM],
            options={
                "require": ["sub", "exp", "type"]
            }
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expirado."
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token inválido."
        )