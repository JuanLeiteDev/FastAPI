from sqlalchemy.orm import mapped_column, Mapped
from app.database.db import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str]
    admin: Mapped[bool] = mapped_column(default=False)
    security_2fa_active: Mapped[bool] = mapped_column(default=False, server_default="0")
    secret_key_2fa: Mapped[str] = mapped_column(default=None, nullable=True)
