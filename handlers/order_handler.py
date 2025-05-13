from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from aiogram.fsm.state import State, StatesGroup

from db.queries.orm import (
    process_table_order,
    check_free_table,
    get_table_order,
    clear_table,
    get_table_foods
)
from keyboards.order_keyboard import (
    get_table_button,
    get_order_button,
    get_count_button,
    get_order_option_button,
    TableCallback,
    ready_order
)

router = Router()


class OrderForm(StatesGroup):
    table_id: str = State()
    food: str = State()
    count: str = State()
    order_foods: dict = State()


def format_order_text(table_id: str, foods: dict) -> str:
    items = "\n".join(f"{k}: {v}" for k, v in foods.items())
    return f"Стол {table_id}\n{items}"


@router.message(Command("Отменить"), OrderForm())
async def cancel_create_order(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(OrderForm.table_id)
    await message.answer("Отменено ❎", reply_markup=get_table_button())

@router.callback_query(TableCallback.filter())
async def table_action(callback: CallbackQuery, callback_data: TableCallback, state: FSMContext):
    table_id = callback_data.table_id
    if callback_data.action == "clear":
        await clear_table(table_id)
        await state.set_state(OrderForm.table_id)

    elif callback_data.action == "edit":
        foods = await get_table_foods(table_id)
        await state.update_data(table_id=table_id, order_foods=foods)
        await state.set_state(OrderForm.food)
        await callback.message.answer(text="Выберите меню:", reply_markup=get_order_button())

    await callback.answer()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Введите номер стола:", reply_markup=get_table_button())
    await state.set_state(OrderForm.table_id)


@router.message(F.text, OrderForm.table_id)
async def handle_table_input(message: Message, state: FSMContext):
    table_id = message.text
    if not await check_free_table(table_id):
        text = await get_table_order(table_id)

        await message.answer(
            text=f"Стол занят\n{text}",
            reply_markup=get_order_option_button(table_id)
        )
    else:
        await state.update_data(table_id=message.text)
        await message.answer(text="Выберите меню:", reply_markup=get_order_button())
        await state.set_state(OrderForm.food)


@router.message(F.text, OrderForm.food)
async def handle_food_selection(message: Message, state: FSMContext):
    text = message.text.strip()
    order = await state.get_data()
    foods = order.get("order_foods", {})
    table_id = order.get("table_id")

    if text == "Сохранить":
        order_text = format_order_text(table_id, foods)
        await message.answer(order_text, reply_markup=get_table_button())
        await message.bot.send_message(
            -4650814133,
            text=f"{order_text}\nСтатус заказа: Активный",
            reply_markup=ready_order()
        )
        await process_table_order(table_id, foods)
        await state.clear()
        await state.set_state(OrderForm.table_id)
        return

    foods[text] = 0
    await state.update_data(order_foods=foods, food=text)

    order_text = format_order_text(table_id, foods)
    await message.answer(order_text, reply_markup=get_count_button())
    await state.set_state(OrderForm.count)


@router.message(F.text, OrderForm.count)
async def handle_food_count_input(message: Message, state: FSMContext):
    order = await state.get_data()
    foods = order.get("order_foods", {})
    food_name = order.get("food")
    table_id = order.get("table_id")

    if not food_name or not table_id:
        await message.answer("Произошла ошибка. Попробуйте снова.")
        await state.set_state(OrderForm.food)
        return

    try:
        count = int(message.text)
        if count == 0:
            foods.pop(food_name, None)
        else:
            foods[food_name] = count
    except ValueError:
        await message.answer("Введите целое число.")
        return

    await state.update_data(order_foods=foods)

    order_text = format_order_text(table_id, foods)
    await message.answer(text=order_text, reply_markup=get_order_button())
    await state.set_state(OrderForm.food)
