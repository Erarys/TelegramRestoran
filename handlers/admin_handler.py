from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile

import pandas as pd

from db.queries.orm import create_report, fill_table, fill_food_menu, get_menu
from filters.base_filters import IsAdmin

class MenuForm(StatesGroup):
    name: str = State()
    price: int = State()

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


@router.message(Command("add_table"))
async def restart_order(message: Message):
    await fill_table()

@router.message(Command("update_menu"))
async def update_menu(message: Message, state: FSMContext):
    await state.clear()
    foods = await get_menu()
    text = "\n".join(f"{food.food_name} {food.price}" for food in foods)

    await message.answer(
        text=f"{text}"
             f"Введите название продукта:"
    )
    await state.set_state(MenuForm.name)

@router.message(F.text, MenuForm.name)
async def food_name(message: Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)

    await message.answer(text="Введите цену:")
    await state.set_state(MenuForm.price)

@router.message(F.text, MenuForm.price)
async def food_price(message: Message, state: FSMContext):
    price = message.text
    await state.update_data(price=price)
    food = await state.get_data()

    if food.get("name") and food.get("price"):
        await fill_food_menu(food.get("name"), food.get("price"))
        await message.answer("Продукт успешно добавлен")
    else:
        await message.answer("Ошибка")