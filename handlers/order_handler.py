from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.state import State, StatesGroup

from db.queries.orm import (
    insert_order,
    fill_table,
    fill_menu, check_free_table, get_table_order, clear_table, get_table_foods
)
from keyboards.order_keyboard import (
    get_table_button,
    get_order_button,
    get_count_button, get_bill_button, TableCallback, ready_order, EditOrderStatusCallback, get_keyboard_fab
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


@router.callback_query(TableCallback.filter())
async def table_callback(callback: CallbackQuery, callback_data: TableCallback, state: FSMContext):
    table_id = callback_data.table_id
    if callback_data.action == "clear":
        await clear_table(table_id)
        await state.set_state(OrderForm.table_id)
    elif callback_data.action == "edit":
        foods = await get_table_foods(table_id)
        await state.update_data(table_id=table_id)
        await state.update_data(order_foods=foods)
        await state.set_state(OrderForm.food)
        await callback.message.answer(text="Выберите меню:", reply_markup=get_order_button())
    await callback.answer()


@router.callback_query(EditOrderStatusCallback.filter())
async def edit_order_status(callback: CallbackQuery, callback_data: EditOrderStatusCallback, state: FSMContext):
    await callback.message.edit_text("Статус заказа: Активный", reply_markup=get_keyboard_fab())


    await callback.answer()


@router.message(F.text, OrderForm.table_id)
async def get_table_id(message: Message, state: FSMContext):
    table_id = message.text
    if not await check_free_table(table_id):
        text = await get_table_order(table_id)

        await message.answer(text=f"Стол занят\n{text}", reply_markup=get_bill_button(table_id))

    else:
        await state.update_data(table_id=message.text)
        await message.answer(text="Выберите меню:", reply_markup=get_order_button())
        await state.set_state(OrderForm.food)


@router.message(F.text, OrderForm.food)
async def get_food(message: Message, state: FSMContext):
    order = await state.get_data()
    foods = order.get("order_foods")

    if message.text == "Сохранить":
        order_text = "".join(f"{k}: {v}\n" for k, v in foods.items())
        await message.answer(f"Стол {order['table_id']}\n{order_text}", reply_markup=get_table_button())
        await message.bot.send_message(
            -4650814133,
            text=f"Стол {order['table_id']}\n{order_text}\nСтатус заказа: Активный",
            reply_markup=ready_order()
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
async def get_food_count(message: Message, state: FSMContext):
    order = await state.get_data()
    foods = order.get("order_foods")

    # Если значение 0, то удаляем данное бюдо
    if message.text.isnumeric():
        if int(message.text) == 0:
            foods.pop(order["food"], None)
        else:
            foods[order["food"]] = int(message.text)
        order_text = "".join(f"{k}: {v}\n" for k, v in foods.items())
        await state.update_data(order_foods=foods)
        await message.answer(text=f"Стол {order['table_id']}\n{order_text}", reply_markup=get_order_button())
        await state.set_state(OrderForm.food)
    else:
        await message.answer("Введите число")
