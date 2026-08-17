from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.models.password_recovery import PasswordRecovery

def add_password_recovery(email: str, hash: str, session: Session):
    new_recovery = PasswordRecovery(
        user_email=email,
        token_hash=hash
    )

    session.add(new_recovery)
    session.commit()


def delete_all_password_recovery(email: str, session: Session):
    session.execute(
        delete(PasswordRecovery)
        .where(PasswordRecovery.user_email == email)
    )
