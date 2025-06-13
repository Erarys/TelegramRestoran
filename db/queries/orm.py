from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.orm import selectinload

from db.database import engine, Base, factory_session
from db.models import OrderFoodORM, FoodsORM, MenuORM, TableORM


async def create_report_period(start_date: datetime, end_date: datetime):
    with factory_session() as session:
        with session.begin():
            orders_dt = dict()

            stmt = (
                select(OrderFoodORM)
                .options(selectinload(OrderFoodORM.foods))
                .where(OrderFoodORM.created_at.between(start_date, end_date))
                .order_by(OrderFoodORM.table_id)
            )
            orders = session.execute(stmt).scalars().all()

            for order in orders:
                orders_dt[order.id] = {
                    "Номер стола": order.table_id,
                    "Официант": order.created_waiter,
                    "Заказ": " - ".join([food.food for food in order.foods]),
                    "Чек": sum([int(food.price_per_unit) for food in order.foods]),
                    "Дата создания": order.created_at,
                }
            print(orders_dt)
            return orders_dt


async def create_report(today: datetime):
    with factory_session() as session:
        with session.begin():
            orders_dt = dict()

            stmt = (
                select(OrderFoodORM)
                .options(selectinload(OrderFoodORM.foods))
                .where(OrderFoodORM.created_at == today)
                .order_by(OrderFoodORM.table_id)
            )
            orders = session.execute(stmt).scalars().all()

            for order in orders:
                orders_dt[order.id] = {
                    "Номер стола": order.table_id,
                    "Официант": order.created_waiter,
                    "Заказ": " - ".join([food.food for food in order.foods]),
                    "Чек": sum([int(food.price_per_unit) for food in order.foods]),
                }

            return orders_dt


async def process_table_order(table_id: int, foods: dict, waiter_name: str, message_id: int):
    with factory_session() as session:
        with session.begin():
            table = session.query(TableORM).filter_by(number=table_id).first()
            if not table:
                raise ValueError(f"Table with id {table_id} not found")

            # Получаем блюда из меню
            foods_objects = {
                food_name: session.query(MenuORM).filter_by(food_name=food_name).first()
                for food_name in foods.keys()
            }

            if table.is_available:
                # Создание нового заказа
                food_entries = [
                    FoodsORM(food=food_name, price_per_unit=menu_obj.price, count=count)
                    for food_name, count in foods.items()
                    if (menu_obj := foods_objects[food_name])  # безопасная проверка существования
                ]
                order = OrderFoodORM(table=table, created_waiter=waiter_name, message_id=message_id)
                order.foods.extend(food_entries)
                session.add(order)
                table.is_available = False

            else:
                # Обновление последнего заказа
                order = (
                    session.query(OrderFoodORM)
                    .filter_by(table_id=table.id, created_waiter=waiter_name)
                    .order_by(OrderFoodORM.created_at.desc())
                    .first()
                )
                if not order:
                    raise ValueError(f"No active order found for table {table_id}")

                order.message_id = message_id
                # Обновляем блюда
                existing_foods = {food.food: food for food in order.foods}
                for food_name, count in foods.items():
                    if food_name in existing_foods:
                        if count == 0:
                            order.foods.remove(existing_foods[food_name])
                        else:
                            existing_foods[food_name].count = count
                    else:
                        menu_obj = foods_objects.get(food_name)

                        if menu_obj:
                            new_food = FoodsORM(
                                food=food_name,
                                price_per_unit=menu_obj.price,
                                count=count
                            )
                            order.foods.append(new_food)

            session.commit()


async def clear_table(table_id):
    with factory_session() as session:
        with session.begin():
            table = session.query(TableORM).filter_by(number=table_id).first()
            if not table.is_available:
                table.is_available = True


async def delete_menu(id: int):
    with factory_session() as session:
        with  session.begin():
            food = session.query(MenuORM).filter_by(id=id).first()
            if food:
                session.delete(food)


async def fill_food_menu(name, price):
    with factory_session() as session:
        with session.begin():
            food = session.query(MenuORM).filter_by(food_name=name).first()
            if food is None:
                food = MenuORM(food_name=name, price=price)
                session.add(food)
                session.commit()
            else:
                return True



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
