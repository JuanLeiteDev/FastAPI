from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, ForeignKey
from app.database.db import Base
from datetime import datetime, timedelta

class TemporaryEmailCode(Base):
    __tablename__ = "temp_email_code"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_email: Mapped[str] = mapped_column(ForeignKey("users.email"))
    temporary_code: Mapped[str | None] = mapped_column(default=None, nullable=True)
    exp: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=lambda: datetime.now() + timedelta(minutes=5)
    )
