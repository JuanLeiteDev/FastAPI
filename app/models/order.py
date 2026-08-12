from sqlalchemy import ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import mapped_column, Mapped
from app.database import Base
from app.config import OrderStatus
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus),
        default=OrderStatus.PENDENTE,
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    price: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
    # items
    