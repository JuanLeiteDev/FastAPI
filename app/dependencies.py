# 1. Importo o criador de sessão
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Cookie, Depends, HTTPException
from app.models import User
from app.services.auth_service import decode_access_token
from app.repository.user_repository import get_user_by_id

# 2. Importo o responsável por criar sessões e que já está ligado com minha base de dados
from app.database import db_engine

def get_session():
    """
    Função responsável por criar sessão e retornar usando o yield para no fim poder fechar a sessão de forma segura
    """
    try:
        Session = sessionmaker(db_engine)
        session = Session()

        yield session
    finally:
        session.close()

def get_current_user(
    access_token: str | None = Cookie(default=None),
    session: Session = Depends(get_session)
) -> User:
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Não autenticado"
        )

    user_id = decode_access_token(access_token)

    user = get_user_by_id(int(user_id), session)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Utilizador não encontrado."
        )

    return user