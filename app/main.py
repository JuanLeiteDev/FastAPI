from fastapi import FastAPI

from app.routers.auth_route import auth_router
from routers.order_route import order_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(order_router)
