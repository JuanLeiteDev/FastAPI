from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from app.database import Base

class OrderItems(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    number_of: Mapped[int]
    flavor: Mapped[str]
    size: Mapped[str]
    unit_price: Mapped[float]
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
