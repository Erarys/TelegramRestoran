from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Для того чтобы alembic видел таблицы
# from db.models import MenuORM, OrderFoodORM, FoodsORM, TableORM