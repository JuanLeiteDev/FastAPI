from app.schemas import UserCreate, UserLogin
from sqlalchemy.orm import Session
from app.models import User
from fastapi import HTTPException
from app.repository import get_user_by_email, create
from app.config import password_hash, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM
from datetime import datetime, timedelta, timezone
import jwt

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

        create(new_user, session)

    session.refresh(new_user)
    return new_user

def authenticate_user(user: UserLogin, session: Session) -> User | None:
    existing_user = get_user_by_email(user.email, session)
    if not existing_user:
        return None

    if not password_hash.verify(user.password, existing_user.password):
        return None

    return existing_user
    

def create_access_token(user: User) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user.id),
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    token = jwt.encode(
        payload=payload,
        key=SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(
            jwt=token,
            algorithms=[ALGORITHM],
            key=SECRET_KEY,
            options={"require": ["sub", "exp"]}
        )

        return payload["sub"]
    
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token inválido."
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expirado."
        )
    except Exception:
        return {"mensagem": "Erro ao tentar decodificar"}

    