from datetime import datetime
from sqlalchemy import desc, select
from sqlalchemy.orm import selectinload
from db.database import engine, Base, factory_session
from db.models import OrderFoodORM, FoodsORM, MenuORM, TableORM


async def create_report_period(start_date: datetime, end_date: datetime):
    async with factory_session() as session:
        orders_dt = dict()

        stmt = (
            select(OrderFoodORM)
            .options(selectinload(OrderFoodORM.foods))
            .where(OrderFoodORM.created_at.between(start_date, end_date))
            .order_by(OrderFoodORM.table_id)
        )
        result = await session.execute(stmt)
        orders = result.scalars().all()

        for order in orders:
            orders_dt[order.id] = {
                "Номер стола": order.table_id,
                "Официант": order.created_waiter,
                "Заказ": " - ".join([food.food for food in order.foods]),
                "Дата создания": order.created_at,
                "Чек": sum([int(food.price_per_unit) for food in order.foods]),
            }

        return orders_dt


async def create_report(today: datetime, tomorrow: datetime) -> dict:
    async with factory_session() as session:
        orders_dt = dict()

        stmt = (
            select(OrderFoodORM)
            .options(selectinload(OrderFoodORM.foods))
            .where(OrderFoodORM.created_at >= today, OrderFoodORM.created_at < tomorrow)
            .order_by(OrderFoodORM.table_id)
        )
        result = await session.execute(stmt)
        orders = result.scalars().all()

        for order in orders:
            orders_dt[order.id] = {
                "Номер стола": order.table_id,
                "Официант": order.created_waiter,
                "Заказ": " - ".join([food.food for food in order.foods]),
                "Чек": sum([food.price_per_unit * food.count  for food in order.foods]),
            }

        return orders_dt


async def create_food_report(today: datetime, tomorrow: datetime, food_names: list[str]):
    async with factory_session() as session:
        orders_dt = dict()

        stmt = (
            select(OrderFoodORM)
            .join(OrderFoodORM.foods)
            .options(selectinload(OrderFoodORM.foods))
            .where(
                OrderFoodORM.created_at >= today,
                OrderFoodORM.created_at < tomorrow,
                FoodsORM.food.in_(food_names)
            )
            .order_by(OrderFoodORM.table_id)
        )

        result = await session.execute(stmt)
        orders = result.scalars().unique().all()

        for order in orders:
            filtered_foods = [food for food in order.foods if food.food in food_names]
            if not filtered_foods:
                continue

            orders_dt[order.id] = {
                "Номер стола": order.table_id,
                "Заказ": ", ".join([f"{food.food} * {food.count}" for food in filtered_foods]),
                "Дата создания": order.created_at,
                "Сумма": sum(food.price_per_unit * food.count for food in filtered_foods),
                "Доля шашлычника": sum(200 * food.count for food in filtered_foods),
            }

        return orders_dt


async def process_table_order(
        table_id: int,
        foods: dict,
        waiter_name: str,
        message_id: int,
        message_id_shashlik: int,
        message_id_lagman: int
    ):

    async with factory_session() as session:
        async with session.begin():
            result = await session.execute(select(TableORM).where(TableORM.number == table_id))
            table = result.scalar_one_or_none()
            if not table:
                raise ValueError(f"Table async with id {table_id} not found")

            foods_objects = {}
            for food_name, food_info in foods.items():
                result = await session.execute(select(MenuORM).where(MenuORM.food_name == food_name))
                foods_objects[food_name] = result.scalar_one_or_none()

            if table.is_available:
                food_entries = [
                    FoodsORM(food=food_name, price_per_unit=menu_obj.price, count=food_info["count"])
                    for food_name, food_info in foods.items()
                    if (menu_obj := foods_objects.get(food_name))
                ]
                order = OrderFoodORM(
                    table=table,
                    created_waiter=waiter_name,
                    message_id=message_id,
                    message_id_shashlik=message_id_shashlik,
                    message_id_lagman=message_id_lagman,
                )

                order.foods.extend(food_entries)
                session.add(order)
                table.is_available = False

            else:
                stmt = (
                    select(OrderFoodORM)
                    .options(selectinload(OrderFoodORM.foods))  # <- вот это важно!
                    .where(OrderFoodORM.table_id == table.id, OrderFoodORM.created_waiter == waiter_name)
                    .order_by(desc(OrderFoodORM.created_at))
                    .limit(1)
                )
                result = await session.execute(stmt)
                order = result.scalar_one_or_none()
                if not order:
                    raise ValueError(f"No active order found for table {table_id}")

                order.message_id = message_id
                order.message_id_shashlik = message_id_shashlik
                order.message_id_lagman = message_id_lagman
                existing_foods = {food.food: food for food in order.foods}

                for food_name, food_info in foods.items():

                    if food_name in existing_foods:
                        if food_info["count"] == 0:
                            order.foods.remove(existing_foods[food_name])
                        else:
                            existing_foods[food_name].count = food_info["count"]
                    else:
                        menu_obj = foods_objects.get(food_name)
                        if menu_obj:
                            new_food = FoodsORM(food=food_name, price_per_unit=menu_obj.price, count=food_info["count"])
                            order.foods.append(new_food)


async def clear_table(table_id):
    async with factory_session() as session:
        async with session.begin():
            result = await session.execute(select(TableORM).where(TableORM.number == table_id))
            table = result.scalar_one_or_none()
            if table and not table.is_available:
                table.is_available = True


async def delete_menu(id: int):
    async with factory_session() as session:
        async with session.begin():
            result = await session.execute(select(MenuORM).where(MenuORM.id == id))
            food = result.scalar_one_or_none()
            if food:
                await session.delete(food)


async def fill_food_menu(name, price):
    async with factory_session() as session:
        async with session.begin():
            result = await session.execute(select(MenuORM).where(MenuORM.food_name == name))
            food = result.scalar_one_or_none()
            if food is None:
                session.add(MenuORM(food_name=name, price=price))
            else:
                return True


async def fill_table(amount: int):
    async with factory_session() as session:
        async with session.begin():
            for number in range(1, amount + 1):
                result = await session.execute(select(TableORM).where(TableORM.number == number))
                table = result.scalar_one_or_none()
                if not table:
                    session.add(TableORM(number=number))


async def restart_table():
    async with factory_session() as session:
        async with session.begin():
            result = await session.execute(select(TableORM))
            tables = result.scalars().all()
            for table in tables:
                table.is_available = True
