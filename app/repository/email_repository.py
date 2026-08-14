from sqlalchemy import select
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
