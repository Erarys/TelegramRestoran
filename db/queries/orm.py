from datetime import datetime

from sqlalchemy import desc, select
from db.database import engine, Base, factory_session
from db.models import OrderFoodORM, FoodsORM, MenuORM, TableORM

async def create_report(start_date: datetime, end_date: datetime):
    with factory_session() as session:
        with session.begin():
            stmt = (
                select(FoodsORM)
                .join(FoodsORM.order)
                .where(OrderFoodORM.created_at.between(start_date, end_date))
            )
            current_order_foods = session.execute(stmt).scalars().all()

            return current_order_foods


async def process_table_order(table_id, foods: dict, waiter_name: str):
    """
    Создаёт или обновляет заказ для указанного стола.
    :param waiter_name: имя сотрудника
    :param table_id: номер стола
    :param foods: словарь с названием блюда и количества {food: count}
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

            order = OrderFoodORM(table=table, created_waiter=waiter_name)

            order.foods.extend(food_entries)
            session.add(order)

            if table.is_available:
                table.is_available = False

            session.commit()


async def clear_table(table_id):
    with factory_session() as session:
        with session.begin():
            table = session.query(TableORM).filter_by(number=table_id).first()
            if not table.is_available:
                table.is_available = True


async def fill_food_menu(name, price):
    with factory_session() as session:
        with session.begin():
            food = MenuORM(food_name=name, price=price)
            session.add(food)
            session.commit()


async def delete_menu(id: int):
    with factory_session() as session:
        with  session.begin():
            food = session.query(MenuORM).filter_by(id=id).first()
            if food:
                session.delete(food)


async def fill_table(amount: int):
    with factory_session() as session:
        with session.begin():
            for number in range(1, amount + 1):
                table = session.query(TableORM).filter_by(number=number).first()
                if table:
                    continue

                table = TableORM(number=number)
                session.add(table)
            session.commit()

