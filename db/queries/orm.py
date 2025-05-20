from datetime import datetime


from sqlalchemy import desc, select
from db.database import engine, Base, factory_session
from db.models import OrderFoodORM, FoodsORM, MenuORM, TableORM

import pandas as pd


async def create_table():
    # Создаем все таблицы наследованные из класса Base
    Base.metadata.create_all(engine)


async def create_report(start_date: datetime, end_date: datetime):
    file_path = f"reports/report_{start_date:%Y%m%d}_{end_date:%Y%m%d}.xlsx"

    print(file_path)

    with factory_session() as session:
        with session.begin():

            stmt = (
                select(FoodsORM)
                .join(FoodsORM.order)
                .where(OrderFoodORM.created_at.between(start_date, end_date))
            )
            current_order_foods = session.execute(stmt).scalars().all()

            ls = []
            for food in current_order_foods:
                ls.append([food.food, food.count, food.price_per_unit])

            sum_food = sum(price * count for food, count, price in ls)
            ls.append(["Сумма всех продаж", "", sum_food])
            df = pd.DataFrame(ls, columns=['Меню', 'кол-во', 'Цена'])
            df.to_excel(file_path)

            return file_path




async def process_table_order(table_id, foods: dict):
    """
    Создаёт или обновляет заказ для указанного стола.
    :param table_id: номер стола
    :param foods: словарь с названием блюда и количеством
    """
    with factory_session() as session:
        with session.begin():
            table = session.query(TableORM).filter_by(number=table_id).first()
            if not table:
                raise ValueError(f"Table with id {table_id} not found")

            # Получаем блюда из меню
            foods_objects = [
                session.query(MenuORM).filter_by(food_name=food).first() for food in foods.keys()
            ]

            food_entries = [
                FoodsORM(food=food_object.food_name, price_per_unit=food_object.price, count=count)
                for food_object, count in zip(foods_objects, foods.values()) if food_object
            ]

            order = OrderFoodORM(table=table)
            order.foods.extend(food_entries)
            session.add(order)

            if table.is_available:
                table.is_available = False

            session.commit()


async def check_free_table(table_id):
    with factory_session() as session:
        with session.begin():
            table = session.query(TableORM).filter_by(number=table_id).first()
            return table.is_available


async def clear_table(table_id):
    with factory_session() as session:
        with session.begin():
            table = session.query(TableORM).filter_by(number=table_id).first()
            if not table.is_available:
                table.is_available = True


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
