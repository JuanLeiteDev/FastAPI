from pydantic import BaseModel

class EmailConfirm(BaseModel):
    code: str