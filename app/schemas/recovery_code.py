from pydantic import BaseModel, Field, field_validator

from app.schemas.user import UserResponse

from app.core.exceptions import InvalidTwoFactorAuthCodeError


class TwoFactorConfirmationRequest(BaseModel):
    otp: str = Field(max_length=6, min_length=6)

    @field_validator("otp", mode="before")
    @classmethod
    def validate_top(cls, value: str):
        value = value.strip()
        if len(value) == 6 and value.isdigit():
            return value

        raise InvalidTwoFactorAuthCodeError

class TwoFactorConfirmationResponse(BaseModel):
    usuario: UserResponse
    codigos: list[str] | None = None
