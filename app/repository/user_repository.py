from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import User

def get_user_by_email(email: str, session: Session) -> User | None:
    return session.scalar(
        select(User).where(User.email == email)
    )

def get_user_by_id(user_id: int, session: Session) -> User | None:
    return session.get(User, user_id)

def create_user(user: User, session: Session):
    session.add(user)
    session.flush()
    return user
