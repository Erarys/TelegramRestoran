from datetime import datetime

from sqlalchemy import desc, select
from db.database import engine, Base, factory_session
from db.models import OrderFoodORM, FoodsORM, MenuORM, TableORM

async def create_table():
    # Создаем все таблицы наследованные из класса Base
    Base.metadata.create_all(engine)