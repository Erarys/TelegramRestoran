from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

import os

MY_URL_PYMYSQL = "mysql+pymysql://{USER}:{PASS}@{HOST}:{PORT}/{NAME}".format(
    HOST=os.getenv("DB_HOST"),
    PORT=os.getenv("DB_PORT"),
    USER=os.getenv("DB_USER"),
    PASS=os.getenv("DB_PASS"),
    NAME=os.getenv("DB_NAME")

)
engine = create_engine(
    url=MY_URL_PYMYSQL,
    echo=True
)

factory_session = sessionmaker(engine)


class Base(DeclarativeBase):
    pass
