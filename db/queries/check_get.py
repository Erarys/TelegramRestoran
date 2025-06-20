from datetime import datetime
from sqlalchemy import desc, select, func
from sqlalchemy.orm import selectinload
from db.database import engine, Base, factory_session
from db.models import OrderFoodORM, FoodsORM, MenuORM, TableORM

# ✅ Получение свободного стола
async def check_free_table(table_id):
    async with factory_session() as session:
        result = await session.execute(
            select(TableORM).where(TableORM.number == table_id)
        )
        table = result.scalar_one_or_none()
        return bool(table and table.is_available)

# ✅ Получение списка блюд по столу
async def get_table_foods(table_id) -> dict:
    async with factory_session() as session:
        table_result = await session.execute(
            select(TableORM).where(TableORM.number == table_id)
        )
        table = table_result.scalar_one_or_none()

        if not table:
            return {}

        order_result = await session.execute(
            select(OrderFoodORM)
            .options(selectinload(OrderFoodORM.foods))  # загрузка связанных блюд
            .where(OrderFoodORM.table == table)
            .order_by(desc(OrderFoodORM.created_at))
            .limit(1)
        )
        order = order_result.scalar_one_or_none()

        if not order:
            return {}

        return {food.food: food.count for food in order.foods}

# ✅ Получение message_id по последнему заказу
async def get_table_order_message(table_id):
    async with factory_session() as session:
        table_result = await session.execute(
            select(TableORM).where(TableORM.number == table_id)
        )
        table = table_result.scalar_one_or_none()

        if not table:
            return None

        order_result = await session.execute(
            select(OrderFoodORM)
            .where(OrderFoodORM.table == table)
            .order_by(desc(OrderFoodORM.created_at))
            .limit(1)
        )
        order = order_result.scalar_one_or_none()

        return order.message_id, order.message_id_shashlik, order if order.message_id_lagman else None

# ✅ Получение счёта
async def get_table_order(table_id):
    async with factory_session() as session:
        table_result = await session.execute(
            select(TableORM).where(TableORM.number == table_id)
        )
        table = table_result.scalar_one_or_none()

        if not table:
            return {}

        order_result = await session.execute(
            select(OrderFoodORM)
            .options(selectinload(OrderFoodORM.foods))
            .where(OrderFoodORM.table == table)
            .order_by(desc(OrderFoodORM.created_at))
            .limit(1)
        )
        order = order_result.scalar_one_or_none()

        if not order:
            return {}

        bill = {
            index: {
                "name": food.food,
                "count": food.count,
                "price": food.price_per_unit,
            }
            for index, food in enumerate(order.foods, start=1)
        }

        return bill

# ✅ Получение меню
async def get_menu(price_from: int, price_to: int) -> dict:
    async with factory_session() as session:
        stmt = select(MenuORM).where(MenuORM.price.between(price_from, price_to))
        result = await session.execute(stmt)
        foods = result.scalars().all()

        return {
            food.id: {
                "name": food.food_name,
                "price": food.price
            } for food in foods
        }


# ✅ Подсчёт количества столов
async def get_table_amount():
    async with factory_session() as session:
        result = await session.execute(select(func.count()).select_from(TableORM))
        count = result.scalar_one()
        return count
