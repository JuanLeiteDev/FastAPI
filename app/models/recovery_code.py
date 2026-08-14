from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from app.database.db import Base
from app.models.user import User

class RecoveryCode(Base):
    __tablename__ = "recovery_codes"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    hash_code: Mapped[str]
    used: Mapped[bool] = mapped_column(default=False)
    user: Mapped["User"] = relationship(back_populates="recovery_code")
    