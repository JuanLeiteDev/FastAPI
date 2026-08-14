from pydantic import BaseModel

class EmailCodeConfirm(BaseModel):
    temporary_code: str
