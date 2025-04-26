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


@router.message(Command("test"))
async def test(message: Message):
    await fill_table()
    await fill_menu()
    await message.answer("Its working..")


@router.message(Command("test2"))
async def test(message: Message):
    table_id = 1
    foods = {
        "Баранина Шашлык": 3
    }
    await insert_order(table_id, foods)
    await message.answer("Its working..")


@router.message(Command("cancel"), OrderForm())
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

    if message.text == "submit":
        await message.answer(f"Стол {order['table_id']} \nВыбрано: {foods}")
        await message.bot.send_message(
            -4650814133,
            text=f"Стол {order['table_id']} \nВыбрано: {foods}",
            parse_mode=ParseMode.HTML
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

        await message.answer(text=f"Выберите количество: \nВыбрано: {foods}", reply_markup=get_count_button())
        await state.set_state(OrderForm.count)


@router.message(F.text, OrderForm.count)
async def get_count(message: Message, state: FSMContext):
    order = await state.get_data()
    foods = order.get("order_foods")

    if message.text.isnumeric():
        foods[order["food"]] = int(message.text)
        await state.update_data(order_foods=foods)
        await message.answer(text=f"Выберите блюда: \nВыбрано: {foods}", reply_markup=get_order_button())
        await state.set_state(OrderForm.food)
    else:
        await message.answer("Введите число")
