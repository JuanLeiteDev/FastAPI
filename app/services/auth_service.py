from app.schemas import UserCreate
from sqlalchemy.orm import Session
from app.models import User
from fastapi import HTTPException
from app.repository import get_user_by_email, create
from app.config import password_hash

def create_account(user: UserCreate, session: Session) -> User:
    with session.begin():
        existing_user = get_user_by_email(user.email, session)

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Já existe um utilizador com este email."
            )

        new_user = User(
            name=user.name,
            email=user.email,
            password=password_hash.hash(user.password)
        )

        create(new_user, session)

    session.refresh(new_user)
    return new_user
