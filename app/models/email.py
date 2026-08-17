from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, ForeignKey
from app.database.db import Base
from datetime import datetime, timedelta, timezone

class TemporaryEmailCode(Base):
    __tablename__ = "TemporaryEmailCode"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_email: Mapped[str] = mapped_column(ForeignKey("Users.email", ondelete="CASCADE"))
    temporary_code: Mapped[str | None] = mapped_column(default=None, nullable=True)
    exp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(minutes=5)
    )
