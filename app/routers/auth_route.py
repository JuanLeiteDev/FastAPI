# 1. Importo o router do fastAPI
from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlalchemy.orm import Session
from app.schemas import UserResponse, UserCreate, UserLogin

from app.models import User
from app.dependencies import get_session, get_current_user
from app.services import create_account, authenticate_user
from app.services.auth_service import create_access_token

# 2. Crio o responsável por criar as rotas de autenticação
auth_router = APIRouter(prefix="/autenticar", tags=["autenticar"])

@auth_router.post("/criar-conta", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    return create_account(user, session)

@auth_router.post("/login", status_code=200)
def login(user: UserLogin, response: Response, session: Session = Depends(get_session)):
    existing_user = authenticate_user(user, session)

    if not existing_user:
        raise HTTPException(
                    status_code=401,
                    detail="Email ou senha incorretos."
                )
    
    access_token = create_access_token(existing_user)  

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=900,
    )

    return {"mensagem": "Login realizado com sucesso."}

@auth_router.get("/me", response_model=UserResponse, status_code=200)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return current_user