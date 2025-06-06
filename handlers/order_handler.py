from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.state import State, StatesGroup

from db.queries.check_get import (
    get_table_foods,
    check_free_table,
    get_table_order,
    get_menu,
    get_table_amount
)

from db.queries.orm import (
    process_table_order,
    clear_table
)
from filters.base_filters import ChatTypeFilter, IsWaiter
from keyboards.order_keyboard import (
    get_table_button,
    get_order_button,
    get_count_button,
    get_order_option_button,
    TableCallback,
    get_order_status_keyboard
)

router = Router()

router.message.filter(ChatTypeFilter(chat_type=["private"]))
router.message.filter(IsWaiter())

class OrderForm(StatesGroup):
    table_id: str = State()
    food: str = State()
    count: str = State()
    order_foods: dict = State()


def format_order_text(table_id: str, foods: dict) -> str:
    text = "\n".join(f"• {name}: {count}шт" for name, count in foods.items())
    return f"<b>Стол:</b> {table_id}\n\n{text}"


@router.message(Command("Отменить"), OrderForm())
async def cancel_create_order(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено ❎")


@router.callback_query(TableCallback.filter())
async def table_action(callback: CallbackQuery, callback_data: TableCallback, state: FSMContext):
    """
    Возможность очищать стол
    редактировать стол, делать новый заказ
    """

    table_id = callback_data.table_id
    if callback_data.action == "clear":
        await clear_table(table_id)
        await state.set_state(OrderForm.table_id)

    elif callback_data.action == "edit":
        foods = await get_table_foods(table_id)
        menu = await get_menu()
        await state.update_data(table_id=table_id, order_foods=foods)
        await state.set_state(OrderForm.food)
        await callback.message.answer(text="Выберите меню:", reply_markup=get_order_button(menu))

    await callback.answer()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    # message.from_user.first_name
    amount = await get_table_amount()
    await message.answer(text=f"<b>Введите номер стола:</b>", reply_markup=get_table_button(amount))
    await state.set_state(OrderForm.table_id)


@router.message(F.text, OrderForm.table_id)
async def table_input(message: Message, state: FSMContext):
    table_id = message.text
    if not table_id or not table_id.strip().isdigit():
        await message.answer("Введите номер стола 🚨")
        return

    if not await check_free_table(table_id):
        bill = await get_table_order(table_id)

        lines = []
        bill_sum = 0

        for index, food in enumerate(bill.values(), start=1):
            count = food.get("count", 0)
            price = food.get("price", 0)
            name = food.get("name", "—")

            summary = price * count
            bill_sum += summary

            lines.append(f"{index}) {name} <i>{count}x{price}</i> = {summary}тг")

        lines.append(f"\n<i>Итого</i>: {bill_sum}тг")
        text = "\n".join(lines)

        await message.answer(
            text=f"<b>Стол занят: {table_id}</b>\n\n{text}",
            reply_markup=get_order_option_button(table_id)
        )
    else:
        await state.update_data(table_id=message.text)
        menu = await get_menu()
        await message.answer(text="Выберите меню:", reply_markup=get_order_button(menu))
        await state.set_state(OrderForm.food)


@router.message(F.text, OrderForm.food)
async def food_selection(message: Message, state: FSMContext):
    text = message.text.strip()
    order = await state.get_data()
    foods = order.get("order_foods", {})
    table_id = order.get("table_id")

    if text == "Сохранить":
        order_text = format_order_text(table_id, foods)
        # Выбираем имя или фамилию работника (выбираем не None)
        waiter_name = message.from_user.first_name or message.from_user.last_name
        amount = await get_table_amount()

        await message.answer(order_text, reply_markup=get_table_button(amount))
        await message.bot.send_message(
            -4951332350,
            text=f"{order_text}\nСтатус заказа: Не готов",
            reply_markup=get_order_status_keyboard(message.from_user.id)
        )
        await process_table_order(table_id, foods, waiter_name)
        await state.clear()
        await state.set_state(OrderForm.table_id)
        return

    foods[text] = 0
    await state.update_data(order_foods=foods, food=text)

    order_text = format_order_text(table_id, foods)
    await message.answer(order_text, reply_markup=get_count_button())
    await state.set_state(OrderForm.count)


@router.message(F.text, OrderForm.count)
async def food_count_input(message: Message, state: FSMContext):
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
    menu = await get_menu()
    await message.answer(text=order_text, reply_markup=get_order_button(menu))
    await state.set_state(OrderForm.food)
