from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select
import os

MY_URL = "mysql+aiomysql://{USER}:{PASS}@{HOST}:{PORT}/{NAME}".format(
    HOST=os.getenv("DB_HOST"),
    PORT=os.getenv("DB_PORT"),
    USER=os.getenv("DB_USER"),
    PASS=os.getenv("DB_PASS"),
    NAME=os.getenv("DB_NAME")
)

engine = create_async_engine(
    url=MY_URL,
    echo=True
)

factory_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass
