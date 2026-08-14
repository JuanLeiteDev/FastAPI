from pydantic import BaseModel

from app.schemas.user import UserResponse


class TwoFactorConfirmationResponse(BaseModel):
    usuario: UserResponse
    codigos: list[str] | None = None
