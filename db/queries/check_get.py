from datetime import datetime

from sqlalchemy import desc, select
from db.database import engine, Base, factory_session
from db.models import OrderFoodORM, FoodsORM, MenuORM, TableORM


async def check_free_table(table_id):
    with factory_session() as session:
        with session.begin():
            table = session.query(TableORM).filter_by(number=table_id).first()
            return table.is_available




async def get_table_foods(table_id):
    with factory_session() as session:
        with session.begin():
            table = session.query(TableORM).filter_by(number=table_id).first()
            order = (
                session.query(OrderFoodORM)
                .filter_by(table=table)
                .order_by(desc(OrderFoodORM.created_at))
                .first()
            )

            return {food.food: food.count for food in order.foods}


async def get_table_order(table_id):
    with factory_session() as session:
        with session.begin():
            table = session.query(TableORM).filter_by(number=table_id).first()
            order = (
                session.query(OrderFoodORM)
                .filter_by(table=table)
                .order_by(desc(OrderFoodORM.created_at))
                .first()
            )

            full_price = 0

            for food in order.foods:
                full_price += food.price_per_unit * food.count
            text = "\n".join(f"{food.food} {food.count} {food.price_per_unit}" for food in order.foods)
            text += f"\nИтого: {full_price}"
            return text


async def get_menu():
    with factory_session() as session:
        with session.begin():
            foods = session.query(MenuORM).all()

        return {
            food.id: {
                "name": food.food_name,
                "price": food.price
            } for food in foods
        }


async def get_table_amount():
    with factory_session() as session:
        return session.query(TableORM).count()