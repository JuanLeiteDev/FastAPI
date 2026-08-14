from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database.db import Base
from typing import List
from app.models.recovery_code import RecoveryCode

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str]
    admin: Mapped[bool] = mapped_column(default=False)
    email_active: Mapped[bool] = mapped_column(default=False, server_default="0")
    security_2fa_active: Mapped[bool] = mapped_column(default=False, server_default="0")
    secret_key_2fa: Mapped[str] = mapped_column(default=None, nullable=True)
    recovery_code: Mapped[List["RecoveryCode"]] = relationship(back_populates="user", cascade="all, delete-orphan")
