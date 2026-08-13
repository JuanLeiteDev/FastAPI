# 1. Importo o FastAPI
from fastapi import FastAPI

# 2. Importo as rotas
from app.routers import auth_router
from app.routers import user_router

# 3. Crio a app
app = FastAPI()

# 4. Incluo as rotas na app
app.include_router(auth_router)
app.include_router(user_router)
