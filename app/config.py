from dotenv import load_dotenv

from enum import Enum
from pwdlib import PasswordHash

import os

load_dotenv()
password_hash = PasswordHash.recommended()

ACCESS_TOKEN_EXPIRE_MINUTES = 1
ALGORITHM = os.getenv("ALGORITHM")
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

class OrderStatus(str, Enum):
    PENDENTE = "PENDENTE"
    PROCESSADO = "PROCESSADO"
    CONFIRMADO = "CONFIRMADO"
    CANCELADO = "CANCELADO"
    