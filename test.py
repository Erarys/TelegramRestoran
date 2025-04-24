from aiogram import Router
from aiogram.enums import ParseMode, ChatAction
from aiogram.filters import CommandStart, Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.redis import RedisStorage

from aiogram import types
from keyboards.order_keyboard import (
    order_callback,
    OrderCallback,
    food_callback,
    FoodCallback,
    count_food,
    FoodCountCallback,
)

router = Router()

class OrderList(StatesGroup):
    table_id = State()
    food = State()
    count = State()

from aiogram.utils.keyboard import ReplyKeyboardBuilder

@router.message(Command("reply_builder"))
async def reply_builder(message: Message):
    builder = ReplyKeyboardBuilder()
    for i in range(1, 17):
        builder.add(types.KeyboardButton(text=str(i)))
    builder.adjust(4)
    await message.answer(
        "Выберите число:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(text="Выберите стол клиента:", reply_markup=order_callback())


@router.callback_query(OrderCallback.filter())
async def make_order(callback: CallbackQuery, callback_data: OrderCallback, state: FSMContext):
    await state.update_data(table_id=callback_data.table_id)
    await callback.message.answer(
        text=f"Выбран стол номером {callback_data.table_id}\nВыберите меню",
        reply_markup=food_callback()
    )
    await callback.answer()
    await state.set_state(OrderList.food)

@router.callback_query(FoodCallback.filter())
async def choose_food(callback: CallbackQuery, callback_data: OrderCallback, state: FSMContext):
    await state.update_data(food=callback_data.food)
    data = await state.get_data()

    if data.get("count", None) is None:
        await state.update_data(count=0)
        data = await state.get_data()

    await callback.answer()
    await callback.message.answer(
        f"Выберите кол-во {data['count']}",
        reply_markup=count_food()
    )


async def update_text(message: Message, new_value: int):
    await message.edit_text(
        f"Выберите кол-во {new_value}",
        reply_markup=count_food()
    )

@router.callback_query(FoodCountCallback.filter())
async def choose_count(callback: CallbackQuery, callback_data: OrderCallback, state: FSMContext):
    action = callback_data.action
    data = await state.get_data()

    await callback.answer()

    if action == "incr":
        await state.update_data(count=data["count"] + 1)
        await update_text(callback.message, data["count"] + 1)
    elif action == "decr":
        if data["count"] > 0:
            await update_text(callback.message, data["count"] + 1)
    else:
        order = await state.get_data()
        text = (
            "<pre>"
            f"Стол {order['table_id']}\n"
            "Товар           | Цена   | Кол-во\n"
            "-----------------------------\n"
            f"{order['food']}| 100 ₽  | {order['count']} шт\n"
            "Сумма| 120 ₽  |\n"
            "</pre>"
        )
        await callback.message.bot.send_message(-4650814133, text=text, parse_mode=ParseMode.HTML)
