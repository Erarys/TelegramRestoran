from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_table_button():
    builder = ReplyKeyboardBuilder()

    for i in range(1, 6):
        builder.add(KeyboardButton(text=str(i)))

    builder.adjust(3)

    return builder.as_markup()

def get_order_button():
    builder = ReplyKeyboardBuilder()
    foods_menu = [
        "Баранина Шашлык",
        "Утка Шашлык",
        "Кока Кола 2л",
        "Чипсы",
        "submit",
        "/cancel"
    ]
    for food in foods_menu:
        builder.add(KeyboardButton(text=str(food)))

    builder.adjust(3)
    return builder.as_markup()

def get_count_button():
    builder = ReplyKeyboardBuilder()

    for i in range(1, 9):
        builder.add(KeyboardButton(text=str(i)))

    builder.adjust(3)

    return builder.as_markup()