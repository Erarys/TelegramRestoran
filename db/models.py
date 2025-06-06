from datetime import datetime
from typing import List

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from db.database import Base


class TableORM(Base):
    __tablename__ = "table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    number: Mapped[int] = mapped_column(unique=True)
    is_available: Mapped[bool] = mapped_column(default=True)

    orders: Mapped[List["OrderFoodORM"]] = relationship(back_populates="table")


class OrderFoodORM(Base):
    __tablename__ = "order_food"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    table_id: Mapped[int] = mapped_column(ForeignKey("table.id"))
    foods: Mapped[List["FoodsORM"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    created_waiter: Mapped[str] = mapped_column(String(length=100))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    table: Mapped["TableORM"] = relationship(back_populates="orders")


class FoodsORM(Base):
    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    food: Mapped[str] = mapped_column(String(length=100))
    count: Mapped[int]
    price_per_unit: Mapped[int]
    order_id: Mapped[int] = mapped_column(ForeignKey("order_food.id"))

    order: Mapped["OrderFoodORM"] = relationship(back_populates="foods")


class MenuORM(Base):
    __tablename__ = "menu"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    food_name: Mapped[str] = mapped_column(String(length=100), unique=True)
    price: Mapped[int]
