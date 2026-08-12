from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import User

def get_user_by_email(email: str, session: Session) -> User | None:
    return session.scalar(
        select(User).where(User.email == email)
    )

def create(user: User, session: Session):
    session.add(user)
    session.flush()
    return user