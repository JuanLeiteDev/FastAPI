# 1. Importo o criador de sessão
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Request, Depends, HTTPException
from app.models import User
from app.security import decode_token
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

def get_user_from_token(token_type: str):

    def dependency(
        request: Request,
        session: Session = Depends(get_session),
    ) -> User:

        token = request.cookies.get(f"{token_type}_token")

        if not token:
            raise HTTPException(
                status_code=401,
                detail="Não autenticado."
            )

        payload = decode_token(token)

        if payload["type"] != token_type:
            raise HTTPException(
                status_code=401,
                detail="Tipo de token inválido."
            )

        user = get_user_by_id(
            int(payload["sub"]),
            session
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="Utilizador não encontrado."
            )

        return user

    return dependency