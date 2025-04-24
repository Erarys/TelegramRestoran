from typing import List

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from db.database import Base


class OrderFoodORM(Base):
    __tablename__ = "order_food"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    table_id: Mapped[int] = mapped_column(primary_key=True)
    foods: Mapped[List["FoodsORM"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class FoodsORM(Base):
    __tablename__ = "foods"
    id: Mapped[int] = mapped_column(primary_key=True,  autoincrement=True)
    food: Mapped[str] = mapped_column(String(length=100))
    count: Mapped[int]
    order_id: Mapped[int] = mapped_column(ForeignKey("order_food.id"))

    order: Mapped["OrderFoodORM"] = relationship(back_populates="foods")
