# 1. Importo o criador de sessão
from sqlalchemy.orm import sessionmaker

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
