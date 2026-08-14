# 1. Importo o criador de sessão
from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from fastapi import Request, Depends, Response, HTTPException
from app.core.config import settings
from app.models.user import User
from app.core.security import decode_token_jwt, create_token_jwt, set_token
from app.repository.user_repository import get_user_by_id
from app.core.exceptions import (
    InvalidJwtTokenError, 
    ExpiredJwtTokenError, 
    UserNotFoundError,
    UnauthenticatedError
)

import jwt

# 2. Importo o responsável por criar sessões e que já está ligado com minha base de dados
from app.database.db import db_engine

def get_session():
    """
    Função responsável por criar sessão e retornar usando o yield para no fim poder fechar a sessão de forma segura
    """
    try:
        session = SessionLocal()

        yield session
    finally:
        session.close()

def get_user_from_temporary(
    request: Request,
    session: Session = Depends(get_session),   
) -> User:

    token = request.cookies.get("temporary_token")

    if not token:
        raise UnauthenticatedError()

    try:
        payload = decode_token_jwt(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expirado."
        )

    if payload["type"] != "temporary":
        raise InvalidJwtTokenError()

    user = get_user_by_id(
        int(payload["sub"]),
        session
    )

    if not user:
        raise UserNotFoundError()

    return user


def get_user_from_access(
    response: Response,
    request: Request,
    session: Session = Depends(get_session),   
) -> User:

    access_token = request.cookies.get("access_token")

    if not access_token:
        raise UnauthenticatedError()

    try:
        payload = decode_token_jwt(access_token)

    except jwt.ExpiredSignatureError:
        return refresh_access(response, request, session)

    if payload["type"] != "access":
        raise InvalidJwtTokenError()

    user = get_user_by_id(
        int(payload["sub"]),
        session
    )

    if not user:
        raise UserNotFoundError()

    return user

def refresh_access(
    response: Response,
    request: Request,
    session: Session
) -> User:

    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise ExpiredJwtTokenError()

    refresh_payload = decode_token_jwt(refresh_token)

    if refresh_payload["type"] != "refresh":
        raise InvalidJwtTokenError()

    user = get_user_by_id(
        int(refresh_payload["sub"]),
        session
    )

    if not user:
        raise UserNotFoundError()

    new_access_token = create_token_jwt(
        user,
        settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        "access"
    )

    set_token(
        response,
        "access_token",
        new_access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return user
