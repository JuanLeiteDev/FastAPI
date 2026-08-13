from app.schemas import UserCreate, UserLogin
from sqlalchemy.orm import Session
from app.models import User
from fastapi import HTTPException
from app.repository.user_repository import get_user_by_email, create_user
from app.security import password_hash
from app.security import setup_2fa, encrypt_secret_2fa, qrcode_generate


def create_account(user: UserCreate, session: Session) -> User:
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

def authenticate_user(user: UserLogin, session: Session) -> User | None:
    existing_user = get_user_by_email(user.email, session)
    if not existing_user:
        return None

    if not password_hash.verify(user.password, existing_user.password):
        return None

    return existing_user


def create_2fa(user: User, session: Session):
    uri, secret = setup_2fa(user)

    secret = encrypt_secret_2fa(secret=secret)
    user.secret_key_2fa = secret
    session.commit()

    return qrcode_generate(uri=uri)
