from app.core.config import settings
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

# Cria conexão com o banco de dados
db_engine = create_engine(
    settings.DATABASE_URL
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=db_engine
)

# Cria a base do banco de dados
Base = declarative_base()
