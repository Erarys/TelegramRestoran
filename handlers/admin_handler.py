from datetime import datetime, timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile

import pandas as pd

from db.queries.orm import create_report
from filters.base_filters import IsAdmin

router = Router()
router.message.filter(IsAdmin())

@router.message(Command("report"))
async def create_order_report(message: Message):
    start_date = datetime.today()
    end_date = datetime.today() - timedelta(days=1)
    file_path = f"reports/report_{start_date:%Y%m%d}_{end_date:%Y%m%d}.xlsx"
    current_order_foods = await create_report(start_date, end_date)

    ls = []
    for food in current_order_foods:
        ls.append([food.food, food.count, food.price_per_unit])

    sum_food = sum(price * count for food, count, price in ls)

    ls.append(["Сумма всех продаж", "", sum_food])

    df = pd.DataFrame(ls, columns=['Меню', 'кол-во', 'Цена'])
    df.to_excel(file_path)

    document = FSInputFile(file_path)
    await message.bot.send_document(message.chat.id, document)


