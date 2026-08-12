from app.config import DATABASE_URL
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine

# Cria conexão com o banco de dados
db_engine = create_engine(DATABASE_URL)

# Cria a base do banco de dados
class Base(DeclarativeBase):
    pass
