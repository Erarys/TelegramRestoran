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
                "Заказ": " - ".join([f"{food.food} x {food.count}" for food in order.foods]),
                "Дата создания": order.created_at,
                "Чек": sum([food.price_per_unit * food.count  for food in order.foods]),
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
                "id": order.id,
                "Номер стола": order.table_id,
                "Официант": order.created_waiter,
                "Заказ": " - ".join([f"{food.food} x {food.count}" for food in order.foods]),
                "Дата создания": order.created_at,
                "Чек": sum([food.price_per_unit * food.count  for food in order.foods]),
            }

        return orders_dt

# Пример: удалить заказы с id в [5, 10]
async def delete_orders(order_ids: list[int]):
    ls = []
    async with factory_session() as session:
        async with session.begin():

            # Получаем нужные заказы
            result = await session.execute(
                select(OrderFoodORM)
                .where(OrderFoodORM.id.in_(order_ids))
                .options(selectinload(OrderFoodORM.foods))  # загружаем связанные foods
            )
            orders = result.scalars().all()

            for order in orders:
                ls.append(order.table_id)
                await session.delete(order)  # автоматически удалит связанные foods
        return ls
        # session.commit() не нужен — уже в контексте begin


from collections import defaultdict

async def create_food_report(today: datetime, tomorrow: datetime, food_names: list[str]):
    async with factory_session() as session:
        orders_dt = dict()
        total_sum = defaultdict(int)  # Автоматически создаёт 0 при первом обращении

        stmt = (
            select(OrderFoodORM)
            .join(OrderFoodORM.foods)
            .options(selectinload(OrderFoodORM.foods))
            .where(
                OrderFoodORM.created_at >= today,
                OrderFoodORM.created_at < tomorrow,
                OrderFoodORM.foods.any(FoodsORM.food.in_(food_names))
            )
            .order_by(OrderFoodORM.table_id)
        )

        result = await session.execute(stmt)
        orders = result.scalars().unique().all()

        for order in orders:
            filtered_foods = [food for food in order.foods if food.food in food_names]
            if not filtered_foods:
                continue

            for food in filtered_foods:
                total_sum[food.food] += food.count  # просто увеличиваем

            orders_dt[order.id] = {
                "Номер стола": order.table_id,
                "Заказ": ", ".join([f"{food.food} * {food.count}" for food in filtered_foods]),
                "Дата создания": order.created_at,
                "Сумма": sum(food.price_per_unit * food.count for food in filtered_foods),
                "Доля шашлычника": sum(200 * food.count for food in filtered_foods),
            }

        return orders_dt, dict(total_sum)  # Преобразуем defaultdict в обычный словарь перед возвратом




async def fill_foods_with_prices(foods: dict) -> dict:
    """
    Получает цены из MenuORM и добавляет их в словарь foods.
    """
    async with factory_session() as session:
        for name, food_data in foods.items():
            result = await session.execute(
                select(MenuORM.price).where(MenuORM.food_name == name)
            )
            price = result.scalar_one_or_none()
            if price is not None:
                food_data["price"] = price
            else:
                food_data["price"] = 0  # если цена не найдена — поставить 0 или можно выкинуть ошибку

        return foods

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
                if message_id_shashlik != 0:
                    order.message_id_shashlik = message_id_shashlik
                if message_id_lagman != 0:
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
                food.price = price
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
