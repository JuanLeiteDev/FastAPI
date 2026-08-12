# 1. Importo o router do fastAPI
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import UserResponse, UserCreate
from app.dependencies import get_session
from app.services import create_account

# 2. Crio o responsável por criar as rotas de autenticação
auth_router = APIRouter(prefix="/autenticar", tags=["autenticar"])

@auth_router.post("/criar-conta", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, session: Session = Depends(get_session)):
    return create_account(user, session)
