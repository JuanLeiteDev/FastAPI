from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.schemas import UserResponse, UserCreate, UserLogin
from app.dependencies import get_session, get_user_from_token
from app.services.auth_service import create_account, authenticate_user, create_2fa
from app.security import create_token, validate_2fa
from app.models import User

auth_router = APIRouter(prefix="/Autenticar", tags=["Autenticar"])

@auth_router.post("/CriarConta", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    return create_account(user, session)

@auth_router.post("/Entrar", status_code=200)
def login(user: UserLogin, response: Response, session: Session = Depends(get_session)):
    existing_user = authenticate_user(user, session)

    if not existing_user:
        raise HTTPException(
                    status_code=401,
                    detail="Email ou senha incorretos."
                )

    token = create_token(existing_user, 2, "temporary")

    response.set_cookie(
        key="temporary_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=900,
        path="/Autenticar"
    )

    return {
        "mensagem": "Autenticação 2FA obrigatória.",
        "active": existing_user.security_2fa_active
    }

@auth_router.post("/Confirmar2FA", status_code=200)
def confirm_2fa(
    otp: str, 
    response: Response, 
    user: User = Depends(get_user_from_token("temporary")), 
    session: Session = Depends(get_session)
):
    if not validate_2fa(user, otp):
        raise HTTPException(
            status_code=401,
            detail="Código inválido"
        )

    if not user.security_2fa_active:
        user.security_2fa_active = True
        session.commit()

    token = create_token(user, 15, "access")

    response.delete_cookie(
        key="temporary_token"
    )
    
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=900,
        path="/"
    )

    return {"mensagem": "Login feito com sucesso"}


@auth_router.post("/Ativar2FA", status_code=200)
def active_security_2fa(
    user: User = Depends(get_user_from_token("temporary")), 
    session: Session = Depends(get_session)
):
    if user.security_2fa_active:
        raise HTTPException(
            status_code=400,
            detail="Autenticação 2FA já foi configurada."
        )
    
    return create_2fa(user, session)