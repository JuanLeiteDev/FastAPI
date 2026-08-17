from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.core.security import password_hash
from app.models.recovery_code import RecoveryCode


def create_many_recovery_code(codes: list[str], user_id: int) -> list[RecoveryCode]:
    return [
        RecoveryCode(
            hash_code=password_hash.hash(code),
            user_id=user_id,
        )
        for code in codes
    ]


def set_many_recovery_code(
    recovery_codes: list[RecoveryCode],
    session: Session,
) -> list[RecoveryCode]:
    session.add_all(recovery_codes)
    session.flush()
    return recovery_codes


def validate_recovery_code(code: str, user_id: int, session: Session) -> bool:
    recovery_codes = session.scalars(
        select(RecoveryCode)
        .where(
            RecoveryCode.user_id == user_id,
        )
    ).all()

    for recovery_code in recovery_codes:
        if password_hash.verify(code, recovery_code.hash_code):
            session.delete(recovery_code)

            session.flush()
            return True

    return False

def delete_recovery_code(code: RecoveryCode, session: Session) -> bool:
    result = session.execute(
        delete(code)
    )

    return result.rowcount > 0