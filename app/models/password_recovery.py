from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, DateTime
from app.database.db import Base
from datetime import datetime, timezone, timedelta

class PasswordRecovery(Base):
    __tablename__ = "PasswordRecovery"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_email: Mapped[str] = mapped_column(
        ForeignKey("Users.email", ondelete="CASCADE"),
        nullable=False
    )
    token_hash: Mapped[str]
    exp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(minutes=15)
    )