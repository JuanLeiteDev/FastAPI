from fastapi import APIRouter, Depends, Response, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserResponse, UserCreate, UserLogin
from app.schemas.email import EmailConfirm
from app.dependencies import get_session, get_user_from_token
from app.services.auth_service import (
    create_account_service, 
    login_service, 
    confirm_2fa_service, 
    active_security_2fa_service,
    send_email_service,
    confirm_email_service
)
from app.models.user import User
from app.repository.email_repository import get_email_by_email

auth_router = APIRouter(prefix="/Autenticar", tags=["Autenticar"])

@auth_router.post("/CriarConta", response_model=UserResponse, status_code=201)
async def create_account(user: UserCreate, session: Session = Depends(get_session)):
    return create_account_service(user, session)



@auth_router.post("/Entrar", status_code=200)
async def login(user: UserLogin, response: Response, session: Session = Depends(get_session)):
    return login_service(user, session, response)



@auth_router.post("/Confirmar2FA", status_code=200, response_model=UserResponse)
async def confirm_2fa(
    otp: str, 
    response: Response, 
    user: User = Depends(get_user_from_token("temporary")), 
    session: Session = Depends(get_session)
):
    return confirm_2fa_service(otp, response, user, session)



@auth_router.post("/Ativar2FA", status_code=200)
async def active_security_2fa(
    user: User = Depends(get_user_from_token("temporary")), 
    session: Session = Depends(get_session)
):
    return active_security_2fa_service(user, session)



@auth_router.post("/ConfirmarEmail", status_code=200, response_model=UserResponse)
async def confirm_email(
    code: EmailConfirm,
    user: User = Depends(get_user_from_token("temporary")),
    session: Session = Depends(get_session)
):
    if user.email_active:
        raise HTTPException(
            status_code=400,
            detail="Email já confirmado."
        )

    existing_temp_email = get_email_by_email(user.email, session)
    if not existing_temp_email:
        raise HTTPException(
            status_code=401,
            detail="Não autenticado."
        )
    
    return confirm_email_service(user, session, code)

@auth_router.post("/EnviarEmail", status_code=200)
async def send_email(
    background_task: BackgroundTasks,
    user: User = Depends(get_user_from_token("temporary")),
    session: Session = Depends(get_session)
):
    if user.email_active:
        raise HTTPException(
            status_code=400,
            detail="Email já confirmado."
        )
        
    background_task.add_task(send_email_service, user, session)

    return {"message": "Email colocado para envio."}

# Refresh Token
# Adicionar secure=True aos tokens
# rate limit
# Validade dos tokens
# Verificar status de administrador
# Verificar email confirmado
# otp em json
# Concorrência
# Esqueci minha senha
# Gerar 6 códigos caso não tenha mais acesso ao 2FA
# Possibilidade de trocar 2FA
# Apagar minha conta