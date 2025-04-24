from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.state import State, StatesGroup

from db.queries.orm import insert_order

router = Router()


class OrderForm(StatesGroup):
    table_id: str = State()
    food: str = State()
    count: str = State()
    order_foods: dict = State()

@router.message(Command("cancel"), OrderForm())
async def cancel_adding_goods(message: Message, state: FSMContext):
    await message.answer("Отменено ❎")
    await state.clear()

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Введите номер стола:")
    await state.set_state(OrderForm.table_id)


@router.message(F.text, OrderForm.table_id)
async def get_table_id(message: Message, state: FSMContext):
    await state.update_data(table_id=message.text)
    await message.answer(text="Выберите меню:")
    await state.set_state(OrderForm.food)


@router.message(F.text, OrderForm.food)
async def get_food(message: Message, state: FSMContext):
    order = await state.get_data()
    foods = order.get("order_foods")

    if message.text == "submit":
        await message.answer(f"Стол {order['table_id']} \nВыбрано: {foods}")
        await insert_order(order["table_id"], foods)
        await state.clear()

    food = message.text
    if isinstance(foods, dict):
        foods[food] = 0
    else:
        foods = {food: 0}

    await state.update_data(order_foods=foods)
    await state.update_data(food=food)

    await message.answer(text=f"Выберите количество: \nВыбрано: {foods}")
    await state.set_state(OrderForm.count)


@router.message(F.text, OrderForm.count)
async def get_count(message: Message, state: FSMContext):
    order = await state.get_data()
    foods = order.get("order_foods")

    if message.text.isnumeric():
        foods[order["food"]] = int(message.text)
    else:
        await message.answer("Введите число")

    await state.update_data(order_foods=foods)
    await message.answer(text=f"Выберите блюда: \nВыбрано: {foods}")
    await state.set_state(OrderForm.food)