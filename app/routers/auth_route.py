from fastapi import APIRouter, BackgroundTasks, Depends, Response
from sqlalchemy.orm import Session
from app.schemas.user import UserResponse, UserCreate, UserLogin
from app.schemas.email import EmailCodeConfirm
from app.schemas.recovery_code import (
    TwoFactorConfirmationRequest,
    TwoFactorConfirmationResponse,
)
from app.schemas.password_recovery import (
    PasswordRecoveryRequest,
    PasswordRecoveryResponse
)
from app.dependencies import get_session, get_user_from_temporary
from app.services.auth_service import (
    create_account_service, 
    login_service, 
    confirm_2fa_service, 
    active_security_2fa_service,
    send_email_service,
    confirm_email_service,
    creat_email,
    password_recovery_service
)
from app.models.user import User
from app.repository.email_repository import get_email_by_user

auth_router = APIRouter(prefix="/Autenticar", tags=["Autenticar"])

@auth_router.post("/CriarConta", status_code=201)
async def create_account(user: UserCreate, session: Session = Depends(get_session)):
    return create_account_service(user, session)



@auth_router.post("/Entrar", status_code=200)
async def login(user: UserLogin, response: Response, session: Session = Depends(get_session)):
    return login_service(user, session, response)



@auth_router.post(
    "/Confirmar2FA",
    status_code=200,
    response_model=TwoFactorConfirmationResponse,
)
async def confirm_2fa(
    confirmation: TwoFactorConfirmationRequest,
    response: Response,
    user: User = Depends(get_user_from_temporary), 
    session: Session = Depends(get_session)
):
    return confirm_2fa_service(confirmation.otp, response, user, session)



@auth_router.post("/Ativar2FA", status_code=200)
async def active_security_2fa(
    user: User = Depends(get_user_from_temporary), 
    session: Session = Depends(get_session)
):
    return active_security_2fa_service(user, session)



@auth_router.post("/ConfirmarEmail", status_code=200)
async def confirm_email(
    code: EmailCodeConfirm,
    user: User = Depends(get_user_from_temporary),
    session: Session = Depends(get_session)
):
    return await confirm_email_service(user, session, code)

@auth_router.post("/EnviarEmail", status_code=200)
async def send_email(
    background_task: BackgroundTasks,
    user: User = Depends(get_user_from_temporary),
    session: Session = Depends(get_session)
):

    config, message = creat_email(user, session)   
    background_task.add_task(send_email_service, config, message)

    return {"message": "Email colocado para envio."}

@auth_router.post("/EsqueciMinhaSenha")
def password_recovery_route(
    email_scheme: PasswordRecoveryRequest,
    response: Response,
    session: Session = Depends(get_session)
):
    return password_recovery_service(email_scheme.email, response, session)

# Adicionar secure=True aos tokens
# rate limit
# Verificar status de administrador
# Concorrência
# Esqueci minha senha
# Apagar minha conta
