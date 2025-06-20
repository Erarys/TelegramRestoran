from logging import exception

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
    get_table_amount, get_table_order_message
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
    get_order_status_keyboard, get_drinks_button
)

router = Router()

router.message.filter(ChatTypeFilter(chat_type=["private"]))
router.message.filter(IsWaiter())


class OrderForm(StatesGroup):
    table_id: str = State()
    food: str = State()
    count: str = State()
    order_foods: dict = State()


def format_order_text(table_id: str, foods: dict, full_name="") -> str:
    text = "\n".join(f"• {name}: {count}шт" for name, count in foods.items())
    return f"<b>Стол:</b> {table_id}\nОфициант: {full_name}\n\n{text}"


def get_diff(new: dict, old: dict) -> dict:
    foods = {}
    for key in new:
        old_count = old.get(key, 0)
        new_count = new[key]
        if new_count != old_count:
            foods[key] = new_count - old_count

    text = "\n".join(
        f"✅ {name}: ➕{count}шт" if count > 0 else f"🔻 {name}: ➖{abs(count)}шт"
        for name, count in foods.items()
    )
    return text


def filter_foods(foods: dict, filter_words: list) -> dict:
    filtered_foods = dict()
    for key in foods.keys():
        if any(word in key for word in filter_words):
            filtered_foods[key] = foods[key]

    return filtered_foods


@router.message(Command("stop"), OrderForm())
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
        menu = await get_menu(1500, 5000)
        await state.update_data(table_id=table_id, order_foods=foods)
        await state.set_state(OrderForm.food)
        await callback.message.answer(text="Выберите меню:", reply_markup=get_order_button(menu))

    await callback.answer()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    # message.from_user.
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
        menu = await get_menu(1500, 5000)
        await message.answer(text="<b>Выберите меню:</b>", reply_markup=get_order_button(menu))
        await state.set_state(OrderForm.food)


@router.message(F.text, OrderForm.food)
async def food_selection(message: Message, state: FSMContext):
    text = message.text.strip()
    order = await state.get_data()
    foods = order.get("order_foods", {})
    table_id = order.get("table_id")

    if text == "save":
        if foods == {}:
            await message.answer("<b>Вы ничего не выбрали❗❗️❗️️</b>")
            return

        f_name = message.from_user.full_name
        foods_shashlik = filter_foods(foods, ["Шашлык"])
        foods_lagman = filter_foods(foods, ["Лагман"])
        msg_shashlik_id = 0
        msg_lagman_id = 0

        order_text = format_order_text(table_id, foods, full_name=f_name)

        # Выбираем имя или фамилию работника (выбираем не None)
        waiter_name = message.from_user.first_name or message.from_user.last_name

        # Функционал отправки заказов поварам
        if not await check_free_table(table_id):
            msg_id, msg_id_shashlik, msg_id_lagman = await get_table_order_message(table_id)
            foods_from_db = await get_table_foods(table_id)
            try:
                await message.bot.delete_message(-4951332350, msg_id)
                if msg_id_shashlik != 0:
                    await message.bot.delete_message(-4921594223, msg_id_shashlik)
                if msg_id_lagman != 0:
                    await message.bot.delete_message(-4907754244, msg_id_lagman)

            except:
                print("Message not found")

            text = get_diff(foods, foods_from_db)
            msg = await message.bot.send_message(
                -4951332350,
                text=f"{order_text}\n\nПохоже официант изменил меню👀 \n{text}\n\nСтатус заказа: Не готов",
                reply_markup=get_order_status_keyboard(message.from_user.id)
            )

            if foods_shashlik != {}:
                order_shashlik_text = format_order_text(table_id, foods_shashlik, full_name=f_name)
                foods_db_shashlik = filter_foods(foods_from_db, ["Шашлык"])
                text_shashlik = get_diff(foods_shashlik, foods_db_shashlik)
                if text_shashlik:
                    msg_shashlik = await message.bot.send_message(
                        -4921594223,
                        text=f"{order_shashlik_text}\n\nПохоже официант изменил меню👀 \n{text_shashlik}\n\nСтатус заказа: Не готов",
                        reply_markup=get_order_status_keyboard(message.from_user.id)
                    )
                    msg_shashlik_id = msg_shashlik.message_id

            if foods_lagman != {}:
                order_lagman_text = format_order_text(table_id, foods_lagman, full_name=f_name)
                foods_db_lagman = filter_foods(foods_from_db, ["Лагман"])
                text_lagman = get_diff(foods_lagman, foods_db_lagman)

                if text_lagman:
                    msg_lagman = await message.bot.send_message(
                        -4907754244,
                        text=f"{order_lagman_text}\n\nПохоже официант изменил меню👀 \n{text_lagman}\n\nСтатус заказа: Не готов",
                        reply_markup=get_order_status_keyboard(message.from_user.id)
                    )
                    msg_lagman_id = msg_lagman.message_id

        else:
            msg = await message.bot.send_message(
                -4951332350,
                text=f"{order_text}\n\nСтатус заказа: Не готов",
                reply_markup=get_order_status_keyboard(message.from_user.id)
            )

            if foods_shashlik != {}:
                order_shashlik_text = format_order_text(table_id, foods_shashlik, full_name=f_name)
                msg_shashlik = await message.bot.send_message(
                    -4921594223,
                    text=f"{order_shashlik_text}\n\nСтатус заказа: Не готов",
                    reply_markup=get_order_status_keyboard(message.from_user.id)
                )
                msg_shashlik_id = msg_shashlik.message_id
            if foods_lagman != {}:
                order_lagman_text = format_order_text(table_id, foods_lagman, full_name=f_name)
                msg_lagman = await message.bot.send_message(
                    -4907754244,
                    text=f"{order_lagman_text}\n\nСтатус заказа: Не готов",
                    reply_markup=get_order_status_keyboard(message.from_user.id)
                )
                msg_lagman_id = msg_lagman.message_id
        # await message.bot.send_message(-4951332350, text, reply_to_message_id=msg.message_id)
        # Тут обращаемся к базе и добавляем заказ или обновляем уже существующий
        try:
            await process_table_order(
                table_id,
                foods,
                waiter_name,
                msg.message_id,
                msg_shashlik_id,
                msg_lagman_id
            )
        except BaseException as exc:
            await message.answer(f"Ошибка ORM❗️\n {exc}")

        await state.clear()
        await state.set_state(OrderForm.table_id)

        # Отправляем занаво кнопки для выбора стола
        amount = await get_table_amount()
        await message.answer(order_text, reply_markup=get_table_button(amount))
        return
    elif text == "Другие товары":
        menu = await get_menu(0, 1500)
        await message.answer("<b>Выберите:</b>", reply_markup=get_drinks_button(menu))
        return
    if foods.get(text, None) is None:
        foods[text] = 0

    await state.update_data(order_foods=foods, food=text)
    f_name = message.from_user.full_name
    order_text = format_order_text(table_id, foods, full_name=f_name)
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
            foods[food_name] = 0
        elif foods.get(food_name, None) is None:
            foods[food_name] = count
        else:
            foods[food_name] += count
    except ValueError:
        await message.answer("Введите целое число.")
        return

    await state.update_data(order_foods=foods)
    f_name = message.from_user.full_name
    order_text = format_order_text(table_id, foods, full_name=f_name)
    menu = await get_menu(1500, 5000)
    await message.answer(text=order_text, reply_markup=get_order_button(menu))
    await state.set_state(OrderForm.food)
