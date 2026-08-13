# 1. Importo o FastAPI
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# 2. Importo as rotas
from app.routers.auth_route import auth_router
from app.routers.user_route import user_router

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

# O frontend e a API compartilham a mesma origem. Isso permite que os cookies
# HttpOnly usados na autenticação sejam enviados automaticamente pelo browser.
frontend_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse(frontend_dir / "index.html")
