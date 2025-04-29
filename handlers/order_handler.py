from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.state import State, StatesGroup

from db.queries.orm import (
    insert_order,
    fill_table,
    fill_menu
)
from keyboards.order_keyboard import (
    get_table_button,
    get_order_button,
    get_count_button,
)

router = Router()


class OrderForm(StatesGroup):
    table_id: str = State()
    food: str = State()
    count: str = State()
    order_foods: dict = State()



@router.message(Command("Отменить"), OrderForm())
async def cancel_adding_goods(message: Message, state: FSMContext):
    await message.answer("Отменено ❎")
    await state.clear()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Введите номер стола:", reply_markup=get_table_button())
    await state.set_state(OrderForm.table_id)


@router.message(F.text, OrderForm.table_id)
async def get_table_id(message: Message, state: FSMContext):
    await state.update_data(table_id=message.text)
    await message.answer(text="Выберите меню:", reply_markup=get_order_button())
    await state.set_state(OrderForm.food)


@router.message(F.text, OrderForm.food)
async def get_food(message: Message, state: FSMContext):
    order = await state.get_data()
    foods = order.get("order_foods")

    if message.text == "Сохранить":
        order_text = "".join(f"{k}: {v}\n" for k, v in foods.items())
        await message.answer(f"Стол {order['table_id']}\n{order_text}", reply_markup=None)
        await message.bot.send_message(
            -4650814133,
            text=f"Стол {order['table_id']}\n{order_text}"
        )
        await insert_order(order["table_id"], foods)
        await state.clear()
    else:
        food = message.text
        if isinstance(foods, dict):
            foods[food] = 0
        else:
            foods = {food: 0}

        await state.update_data(order_foods=foods)
        await state.update_data(food=food)
        order_text = "".join(f"{k}: {v}\n" for k, v in foods.items())
        await message.answer(text=f"Стол {order['table_id']}\n{order_text}", reply_markup=get_count_button())
        await state.set_state(OrderForm.count)


@router.message(F.text, OrderForm.count)
async def get_count(message: Message, state: FSMContext):
    order = await state.get_data()
    foods = order.get("order_foods")

    if message.text.isnumeric():
        foods[order["food"]] = int(message.text)
        order_text = "".join(f"{k}: {v}\n" for k, v in foods.items())
        await state.update_data(order_foods=foods)
        await message.answer(text=f"Стол {order['table_id']}\n{order_text}", reply_markup=get_order_button())
        await state.set_state(OrderForm.food)
    else:
        await message.answer("Введите число")
