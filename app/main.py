# 1. Importo o FastAPI
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# 2. Importo as rotas
from app.routers.auth_route import auth_router
from app.routers.user_route import user_router

from app.core import handlers as ha

# 3. Crio a app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Incluo as rotas na app
app.include_router(auth_router)
app.include_router(user_router)

app.add_exception_handler(
    ha.TwoFactorAuthNotConfiguredError,
    ha.not_configured_2fa_handler
)
app.add_exception_handler(
    ha.InvalidTwoFactorAuthCodeError,
    ha.invalid_2fa_code_handler
)
app.add_exception_handler(
    ha.UserAlreadyExistsError,
    ha.user_already_exists_handler
)
app.add_exception_handler(
    ha.UserNotFoundError,
    ha.user_not_found_handler
)
app.add_exception_handler(
    ha.InvalidTokenError,
    ha.invalid_jwt_token_handler
)

app.add_exception_handler(
    ha.InvalidEmailOrPasswordError,
    ha.invalid_email_password_handler
)

app.add_exception_handler(
    ha.EmailConfirmationRequiredError,
    ha.email_confirmation_required_handler
)

app.add_exception_handler(
    ha.TwoFactorAuthAlreadyConfiguredError,
    ha.already_2fa_configured_handler
)

app.add_exception_handler(
    ha.EmailAlreadyConfirmedError,
    ha.email_already_confirmed_handler
)

app.add_exception_handler(
    ha.InvalidEmailConfirmationCodeError,
    ha.invalid_email_code_handler
)

app.add_exception_handler(
    ha.ExpiredEmailConfirmationCodeError,
    ha.expired_email_code_handler
)

app.add_exception_handler(
    ha.InvalidJwtTokenError,
    ha.invalid_jwt_token_handler
)

app.add_exception_handler(
    ha.ExpiredJwtTokenError,
    ha.expired_jwt_token_handler
)

app.add_exception_handler(
    ha.UnauthenticatedError,
    ha.unauthenticated_handler
)

# O frontend e a API compartilham a mesma origem. Isso permite que os cookies
# HttpOnly usados na autenticação sejam enviados automaticamente pelo browser.
frontend_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse(frontend_dir / "index.html")


# Rotas de navegação do frontend. Todas entregam a mesma aplicação e permitem
# atualizar ou partilhar um endereço sem receber 404 do servidor.
@app.get("/entrar", include_in_schema=False)
@app.get("/criar-conta", include_in_schema=False)
@app.get("/confirmar-email", include_in_schema=False)
@app.get("/confirmar-2fa", include_in_schema=False)
@app.get("/minha-conta", include_in_schema=False)
def frontend_route():
    return FileResponse(frontend_dir / "index.html")
