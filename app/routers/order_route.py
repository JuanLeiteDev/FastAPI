#1. Importo o router do FastAPI
from fastapi import APIRouter

# 2. Crio o responsável por criar as rotas de pedidos
order_router = APIRouter(prefix="/pedidos", tags=["pedidos"])
