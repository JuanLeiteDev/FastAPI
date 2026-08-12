# 1. Importo o load_dotenv para carregar váriaveis do .env
from dotenv import load_dotenv

from enum import Enum
from pwdlib import PasswordHash

# 2. Importo os
import os

# 3. Carrego variáveis do .env
load_dotenv()
password_hash = PasswordHash.recommended()

# 4. Pego as variáveis necessárias
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

# Classe para definir status do pedido
class OrderStatus(str, Enum):
    PENDENTE = "PENDENTE"
    PROCESSADO = "PROCESSADO"
    CONFIRMADO = "CONFIRMADO"
    CANCELADO = "CANCELADO"
    