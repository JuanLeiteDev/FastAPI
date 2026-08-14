from pydantic import BaseModel, Field

class RecoveryCodeCreate(BaseModel):
    hash_code: str = Field(max_length=16, min_length=16)
    user_id: int
    