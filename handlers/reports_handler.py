from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile

from db.queries.orm import create_report

router = Router()


@router.message(Command("today_report"))
async def create_order_report(message: Message):
    start_date = datetime(2025, 3, 29)
    end_date = datetime(2025, 6, 30)

    path = await create_report(start_date, end_date)
    document = FSInputFile(path)

    await message.bot.send_document(message.chat.id, document)
