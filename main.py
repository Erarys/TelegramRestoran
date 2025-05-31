from dotenv import load_dotenv
load_dotenv()

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from db.database import Base, engine
# from db.queries.orm import create_table
from handlers import (
    order_handler,
    order_for_cook,
    admin_handler
)

import os
import asyncio
import logging

storage = RedisStorage.from_url("redis://localhost:6379/0")

async def main():
    """
    Самый основной функция
    Соединяет все роутеры к диспетчеру
    :return:
    """
    bot = Bot(token=os.getenv("TOKEN"))

    # Clear the fsm storage
    redis = await storage.redis
    keys = await redis.keys("fsm:*")
    if keys:
        await redis.delete(*keys)

    dp = Dispatcher(storage=storage)
    dp.include_router(order_handler.router)
    dp.include_router(order_for_cook.router)
    dp.include_router(admin_handler.router)
    # Base.metadata.drop_all(bind=engine)  # Удаляет все таблицы
    # Base.metadata.create_all(bind=engine)  # Создает их заново по моделям
    # await create_table()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
