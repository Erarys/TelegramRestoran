from aiogram import Bot, Router
from aiogram.types import BotCommand


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="stop", description="Отменить создание заказа"),
    ]
    await bot.set_my_commands(commands)
