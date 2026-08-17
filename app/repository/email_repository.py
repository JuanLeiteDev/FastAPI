from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.models.email import TemporaryEmailCode

def create_temp_email(info: TemporaryEmailCode, session: Session):
    existing_temp_email = get_email_by_user(info.user_email, session)
    if existing_temp_email:
        session.delete(existing_temp_email)
    
    session.add(info)
    session.commit()
    return info

def get_email_by_user(user_email: str, session: Session) -> TemporaryEmailCode | None: 
    return session.scalar(
        select(TemporaryEmailCode)
        .where(TemporaryEmailCode.user_email == user_email)
    )

def delete_temporary_email(user_email: str, session: Session) -> bool:
    result = session.execute(
        delete(TemporaryEmailCode)
        .where(TemporaryEmailCode.user_email == user_email)
    )

    session.flush()

    return result.rowcount > 0
