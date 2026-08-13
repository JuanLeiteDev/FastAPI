from fastapi import APIRouter, Depends, Response, Request
from app.schemas.user import UserResponse
from app.models.user import User
from app.dependencies import get_user_from_token

user_router = APIRouter(prefix="/MinhaConta", tags=["user"])

@user_router.get("/", response_model=UserResponse, status_code=200)
def get_me(current_user: User = Depends(get_user_from_token("access"))) -> UserResponse:
    return current_user

@user_router.post("/Sair", status_code=200)
def logout(response: Response, _: User = Depends(get_user_from_token("access"))): 
    response.delete_cookie("access_token")
    response.delete_cookie("temporary_token", path="/Autenticar")

    return {"mensagem": "Logout feito com sucesso."}
