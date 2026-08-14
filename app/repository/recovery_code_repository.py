from sqlalchemy.orm import Session
from sqlalchemy import select
from app.schemas.recovery_code import RecoveryCodeCreate
from app.models.recovery_code import RecoveryCode
from app.core.security import password_hash
from typing import List
from app.models.user import User

def set_many_recovery_code(recovery_codes: List[RecoveryCode], session: Session):
    session.add_all(recovery_codes)
    session.commit()
    return recovery_codes

def create_many_recovery_code(codes: str, user_id: int):
    new_codes = []
    for code in codes:
        new_recovery_code = RecoveryCodeCreate()
        new_recovery_code.hash_code = password_hash.hash(code)
        new_recovery_code.user_id = user_id
        new_codes.append(new_recovery_code)

    return new_codes

def valide_recovery_code(code: str, user: User, session: Session):
    existing_recovery_code = session.scalar(
        select(RecoveryCode)
        .where(
            RecoveryCode.user_id == user.id and 
            password_hash.verify(code, RecoveryCode.hash_code)
        )
    )

    if existing_recovery_code:
        existing_recovery_code.used = True
        return True
    return False
    