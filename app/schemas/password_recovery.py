from pydantic import BaseModel, EmailStr

class PasswordRecoveryRequest(BaseModel):
    email: EmailStr

class PasswordRecoveryResponse(BaseModel):
    link_password_recovery: str
