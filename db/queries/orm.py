from sqlalchemy import select, and_, delete, func
from db.database import engine, Base, factory_session
from db.models import OrderFoodORM, FoodsORM
from typing import List


async def create_table():
    # Создаем все таблицы наследованные из класса Base
    Base.metadata.create_all(engine)

async def insert_order(table_id, foods: dict):
    with factory_session() as session:
        with session.begin():
            order = OrderFoodORM(
                table_id=int(table_id),
            )
            order.foods = [
                FoodsORM(food=food, count=count) for food, count in foods.items()
            ]

            session.add(order)
            session.commit()




