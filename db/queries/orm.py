from sqlalchemy import select, and_, delete, func
from db.database import engine, Base, factory_session
from db.models import OrderFoodORM, FoodsORM, MenuORM, TableORM
from typing import List


async def create_table():
    # Создаем все таблицы наследованные из класса Base
    Base.metadata.create_all(engine)

# async def insert_order(table_id, foods: dict):
#     with factory_session() as session:
#         with session.begin():
#             order = OrderFoodORM(
#                 table_id=int(table_id),
#             )
#             order.foods = [
#                 FoodsORM(food=food, count=count) for food, count in foods.items()
#             ]
#
#             session.add(order)
#             session.commit()

async def insert_order(table_id, foods: dict):

    with factory_session() as session:
        with session.begin():
            table = session.query(TableORM).filter_by(number=table_id).first()
            if table.is_available:
                table.is_available = False
                order = OrderFoodORM(table=table)

                foods_objects = [session.query(MenuORM).filter_by(food_name=food).first() for food in foods.keys()]
                order.foods = [
                    FoodsORM(food=food_object.food_name, price_per_unit=food_object.price, count=count) for food_object, count in zip(foods_objects, foods.values())
                ]
                session.add(order)
                session.commit()



async def fill_menu():
    with factory_session() as session:
        with session.begin():
            foods_menu = {
                "Баранина Шашлык": 1800,
                "Утка Шашлык": 1600,
                "Кока Кола 2л": 1000,
                "Чипсы": 500,
            }
            for name, price in foods_menu.items():
                food = MenuORM(food_name=name, price=price)
                session.add(food)
            session.commit()

async def fill_table():
    with factory_session() as session:
        with session.begin():
            ls = list(range(1, 6))
            for index in ls:
                table = TableORM(number=index)
                session.add(table)
            session.commit()