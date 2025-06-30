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
    get_table_amount, get_table_order_message
)

from db.queries.orm import (
    process_table_order,
    clear_table
)
from filters.base_filters import ChatTypeFilter, IsWaiter
from keyboards.order_keyboard import (
    get_table_button,
    get_count_button,
    get_order_option_button,
    TableCallback,
    get_order_status_keyboard,
    choose_food_type,
    choose_shashlik_food,
    choose_lagman_food,
    choose_dishes_food,
    choose_selad_food,
    choose_garnish_food,
    choose_garnish_additional,
    choose_drinks,
    choose_snacks, choose_bear
)

router = Router()

router.message.filter(ChatTypeFilter(chat_type=["private"]))
router.message.filter(IsWaiter())


class OrderForm(StatesGroup):
    table_id: str = State()
    food_type: str = State()
    food: str = State()
    garnish: str = State()
    count: str = State()
    order_foods: dict = State()


filter_for_lagman = [
    "Гуйру",
    "Суйру",
    "Домашний лагман",
    "Гуйру цомян",
    "Дин-дин",
    "Лагман с ребрами",
    "Могру",
    "Хаухуа",
    "Мошру",
    "Фирменный лагман \"Арыс\"",
    "Красные пельмени",
    "Мампар",
    "Суп с мясом",
    "Пельмень",
    "Фри с мясом",
    "Мясо по-тайски",
    "Мушуру сай",
    "Могуру сай",
    "Казан-кебаб",
    "Дапанджи",
    "Свежий салат",
    "Пекинский салат",
    "Хрустящий баклажан",
    "Ачучук",
    "Фри"
]
filter_for_shashlik = [
    "Баранина",
    "Утка",
    "Крылочка",
    "Люля",
    "Ребра",
    "Антрекот",
    "Говядина",
]


def format_order_text(table_id: str, foods: dict, full_name="") -> str:
    text = "\n".join(
        f"• {name}: {food_info['count']}шт"
        for name, food_info in foods.items()
    )
    return f"<b>Стол:</b> {table_id}\nОфициант: {full_name}\n\n{text}"

def format_order_text_with_price(table_id: str, foods: dict, full_name="") -> str:
    lines = [f"<b>Стол:</b> {table_id}", f"<b>Официант:</b> {full_name}", ""]

    bill_sum = 0
    for name, food_info in foods.items():
        count = food_info.get("count", 0)
        price = food_info.get("price", 0)
        summary = count * price
        bill_sum += summary

        lines.append(f"• {name}: <i>{count}x{price}</i> = {summary}тг")

    lines.append(f"\n<b>Итого:</b> {bill_sum}тг")
    return "\n".join(lines)



def get_diff(new: dict, old: dict) -> dict:
    foods = {}
    for key in new:
        old_count = old.get(key, {}).get("count", 0)
        new_count = new[key]["count"]
        if new_count != old_count:
            foods[key] = {
                "count": new_count - old_count,
                "garnish": new[key].get("garnish", ""),

            }

    text = "\n".join(
        f"✅ {name}: ➕{food_info['count']}шт" if food_info['count'] > 0 else f"🔻 {name}: ➖{abs(food_info['count'])}шт"
        for name, food_info in foods.items()
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


@router.message(Command("back"))
async def back_to_menu(message: Message, state: FSMContext):
    await message.answer(text="<b>Выберите категорию</b>", reply_markup=choose_food_type())
    await state.set_state(OrderForm.food_type)


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
        await state.update_data(table_id=table_id, order_foods=foods)
        await state.set_state(OrderForm.food)
        await callback.message.answer(text="<b>Выберите категорию</b>", reply_markup=choose_food_type())
        await state.set_state(OrderForm.food_type)

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
        await message.answer(text="<b>Выберите категорию</b>", reply_markup=choose_food_type())
        await state.set_state(OrderForm.food_type)


@router.message(F.text, OrderForm.food_type)
async def food_type(message: Message, state: FSMContext):
    text = message.text.strip()

    order = await state.get_data()
    foods = order.get("order_foods", {})
    table_id = order.get("table_id")
    f_name = message.from_user.full_name
    foods_shashlik = filter_foods(foods, filter_for_shashlik)

    foods_lagman = filter_foods(foods, filter_for_lagman)

    if text == "save":
        if foods == {}:
            await message.answer("<b>Вы ничего не выбрали❗❗️❗️️</b>")
            return

        msg_shashlik_id = 0
        msg_lagman_id = 0

        order_text = format_order_text_with_price(table_id, foods, full_name=f_name)

        # Выбираем имя или фамилию работника (выбираем не None)
        waiter_name = message.from_user.first_name or message.from_user.last_name

        # Функционал отправки заказов поварам
        if not await check_free_table(table_id):
            msg_id, msg_id_shashlik, msg_id_lagman = await get_table_order_message(table_id)
            foods_from_db = await get_table_foods(table_id)

            text = get_diff(foods, foods_from_db)

            msg = await message.bot.send_message(
                -4773383218,
                text=f"{order_text}\n\nПохоже официант изменил меню👀 \n{text}\n\nСтатус заказа: Не готов",
                reply_markup=get_order_status_keyboard(message.from_user.id)
            )
            if text:
                try:
                    await message.bot.delete_message(-4773383218, msg_id)
                except:
                    pass


            if foods_shashlik != {}:
                order_shashlik_text = format_order_text(table_id, foods_shashlik, full_name=f_name)
                foods_db_shashlik = filter_foods(foods_from_db, filter_for_shashlik)

                text_shashlik = get_diff(foods_shashlik, foods_db_shashlik)
                if text_shashlik:
                    try:
                        await message.bot.delete_message(-4921594223, msg_id_shashlik)
                    except:
                        pass
                    msg_shashlik = await message.bot.send_message(
                        -4921594223,
                        text=f"{order_shashlik_text}\n\nПохоже официант изменил меню👀 \n{text_shashlik}\n\nСтатус заказа: Не готов",
                        reply_markup=get_order_status_keyboard(message.from_user.id)
                    )
                    msg_shashlik_id = msg_shashlik.message_id

            if foods_lagman != {}:
                order_lagman_text = format_order_text(table_id, foods_lagman, full_name=f_name)
                foods_db_lagman = filter_foods(foods_from_db, filter_for_lagman)
                text_lagman = get_diff(foods_lagman, foods_db_lagman)

                if text_lagman:
                    try:
                        await message.bot.delete_message(-4815751000, msg_id_lagman)
                    except:
                        pass
                    msg_lagman = await message.bot.send_message(
                        -4815751000,
                        text=f"{order_lagman_text}\n\nПохоже официант изменил меню👀 \n{text_lagman}\n\nСтатус заказа: Не готов",
                        reply_markup=get_order_status_keyboard(message.from_user.id)
                    )
                    msg_lagman_id = msg_lagman.message_id

        else:
            msg = await message.bot.send_message(
                -4773383218,
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
                    -4815751000,
                    text=f"{order_lagman_text}\n\nСтатус заказа: Не готов",
                    reply_markup=get_order_status_keyboard(message.from_user.id)
                )
                msg_lagman_id = msg_lagman.message_id

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

    if text == "Шашлык 🍢":
        await message.answer("<b>Выберите меню:</b>", reply_markup=choose_shashlik_food())
    elif text == "Лагман 🍜":
        await message.answer("<b>Выберите меню:</b>", reply_markup=choose_lagman_food())
    elif text == "Горячие Блюда 🐦‍🔥":
        await message.answer("<b>Выберите меню:</b>", reply_markup=choose_dishes_food())
    elif text == "Салаты 🥗":
        await message.answer("<b>Выберите меню:</b>", reply_markup=choose_selad_food())
    elif text == "Напитки 🥤":
        await message.answer("<b>Выберите меню:</b>", reply_markup=choose_drinks())
    elif text == "Закуски 🍟":
        await message.answer("<b>Выберите меню:</b>", reply_markup=choose_snacks())
    elif text == "Пиво 🍺":
        await message.answer("<b>Выберите меню:</b>", reply_markup=choose_bear())
    if text == "Блюда с гарниром 🍛":
        await message.answer("<b>Выберите меню:</b>", reply_markup=choose_garnish_food())
        await state.update_data(food_type="pair")
    else:
        await state.update_data(food_type="single")

    await state.set_state(OrderForm.food)


@router.message(F.text, OrderForm.food)
async def food_selection(message: Message, state: FSMContext):
    food_name = message.text.strip()
    order = await state.get_data()
    foods = order.get("order_foods", {})
    table_id = order.get("table_id")

    if foods.get(food_name, None) is None:
        foods[food_name] = {"count": 0, "garnish": None}

    await state.update_data(order_foods=foods, food=food_name)

    # Если это лагман с гарниром, то еще выбераем гарнир
    if order["food_type"] == "pair":
        await message.answer("Введите гарнир", reply_markup=choose_garnish_additional())
        await state.set_state(OrderForm.garnish)
        return

    f_name = message.from_user.full_name
    order_text = format_order_text(table_id, foods, full_name=f_name)
    await message.answer(order_text, reply_markup=get_count_button())
    await state.set_state(OrderForm.count)


@router.message(F.text, OrderForm.garnish)
async def select_garnish(message: Message, state: FSMContext):
    garnish = message.text.strip()
    order = await state.get_data()
    food_name = order["food"]
    foods = order.get("order_foods", {})
    table_id = order.get("table_id")
    value = foods.pop(food_name, {"count": 0, "garnish": None})
    food_name = f"{food_name} ({garnish})"
    foods[food_name] = value

    await state.update_data(order_foods=foods, garnish=garnish, food=food_name)
    f_name = message.from_user.full_name
    order_text = format_order_text(table_id, foods, full_name=f_name)
    await message.answer(order_text, reply_markup=get_count_button())
    await state.set_state(OrderForm.count)


@router.message(F.text, OrderForm.count)
async def food_count_input(message: Message, state: FSMContext):
    order = await state.get_data()
    foods = order.get("order_foods", {})
    food_name = order.get("food")
    garnish = order.get("garnish", None)
    table_id = order.get("table_id")

    if not food_name or not table_id:
        await message.answer("Произошла ошибка. Попробуйте снова.")
        await state.set_state(OrderForm.food)
        return

    try:
        count = int(message.text)
        if count == 0:
            foods[food_name] = {
                "count": 0,
                "garnish": garnish
            }
        elif foods.get(food_name, None) is None:
            foods[food_name] = {
                "count": count,
                "garnish": garnish
            }
        else:
            foods[food_name]["count"] += count

    except ValueError:
        await message.answer("Введите целое число.")
        return

    await state.update_data(order_foods=foods)
    f_name = message.from_user.full_name
    order_text = format_order_text(table_id, foods, full_name=f_name)
    await message.answer(text=order_text, reply_markup=choose_food_type())
    await state.set_state(OrderForm.food_type)
