from fastapi import Request
from fastapi.responses import JSONResponse
from jwt import InvalidTokenError, ExpiredSignatureError

from app.core.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidTwoFactorAuthCodeError,
    TwoFactorAuthNotConfiguredError,
    InvalidEmailOrPasswordError,
    EmailConfirmationRequiredError,
    TwoFactorAuthAlreadyConfiguredError,
    EmailAlreadyConfirmedError,
    InvalidEmailConfirmationCodeError,
    ExpiredEmailConfirmationCodeError
)

async def user_not_found_handler(
    request: Request,
    exc: UserNotFoundError
):
    return JSONResponse(
        status_code=404,
        content={"detail": "Usuário não encontrado."}
    )
async def user_already_exists_handler(
    request: Request,
    exc: UserAlreadyExistsError
):
    return JSONResponse(
        status_code=409,
        content={"detail": "Usuário já existe."}
    )
async def invalid_2fa_code_handler(
    request: Request,
    exc: InvalidTwoFactorAuthCodeError
):
    return JSONResponse(
        status_code=401,
        content={"detail": "Código inválido."}
    )
async def not_configured_2fa_handler(
    request: Request,
    exc: TwoFactorAuthNotConfiguredError
):
    return JSONResponse(
        status_code=400,
        content={"detail": "Autenticação 2FA ainda não foi configurada."}
    )
async def invalid_jwt_token_handler(
    request: Request,
    exc: InvalidTokenError
):
    return JSONResponse(
        status_code=401,
        content={"detail": "Token inválido."}
    )
async def expired_jwt_token_handler(
    request: Request,
    exc: ExpiredSignatureError
):
    return JSONResponse(
        status_code=401,
        content={"detail": "Token expirado."}
    )
async def invalid_email_password_handler(
    request: Request,
    exc: InvalidEmailOrPasswordError
):
    return JSONResponse(
        status_code=400,
        content={"detail": "Email ou senha incorretos."}
    )
async def email_confirmation_required_handler(
    request: Request,
    exc: EmailConfirmationRequiredError
):
    return JSONResponse(
        status_code=401,
        content={"detail": "É obrigatório a confirmação do e-mail primeiro."}
    )
async def already_2fa_configured_handler(
    request: Request,
    exc: TwoFactorAuthAlreadyConfiguredError
):
    return JSONResponse(
        status_code=400,
        content={"detail": "Autenticação 2FA já foi configurada."}
    )
async def email_already_confirmed_handler(
    request: Request,
    exc: EmailAlreadyConfirmedError
):
    return JSONResponse(
        status_code=400,
        content={"detail": "Email já confirmado."}
    )
async def invalid_email_code_handler(
    request: Request,
    exc: InvalidEmailConfirmationCodeError
):
    return JSONResponse(
        status_code=401,
        content={"detail": "Código inválido."}
    )
async def expired_email_code_handler(
    request: Request,
    exc: ExpiredEmailConfirmationCodeError
):
    return JSONResponse(
        status_code=401,
        content={"detail": "Código expirado."}
    )
