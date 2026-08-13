from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.email import TemporaryEmail

def create_email_repository(email: TemporaryEmail, session: Session):
    existing_email = get_email_by_email(email.user_email, session)
    if existing_email:
        session.delete(existing_email)
    
    session.add(email)
    session.commit()
    return email

def get_email_by_email(email: str, session: Session) -> TemporaryEmail | None: 
    return session.scalar(
        select(TemporaryEmail)
        .where(TemporaryEmail.user_email == email)
    )
