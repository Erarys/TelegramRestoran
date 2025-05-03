from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


class TableCallback(CallbackData, prefix="table"):
    action: str
    table_id: str

class EditOrderStatusCallback(CallbackData, prefix="edit_status"):
    status: str

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
        "Сохранить",
        "/Отменить"
    ]
    for food in foods_menu:
        builder.add(KeyboardButton(text=str(food)))

    builder.adjust(3)
    return builder.as_markup()

def get_count_button():
    builder = ReplyKeyboardBuilder()

    for i in range(0, 9):
        builder.add(KeyboardButton(text=str(i)))

    builder.adjust(3)

    return builder.as_markup()

def get_bill_button(table_id) -> InlineKeyboardButton:
    buttons = [
        [
            InlineKeyboardButton(
                text="🧹 Очистить стол",
                callback_data=TableCallback(action="clear", table_id=table_id).pack()
            ),
            InlineKeyboardButton(
                text="🧾 Чек",
                callback_data=TableCallback(action="bill", table_id=table_id).pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="📝 Редактировать",
                callback_data=TableCallback(action="edit", table_id=table_id).pack()
            )
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard

def ready_order() -> InlineKeyboardButton:
    buttons = [
            [
                InlineKeyboardButton(
                    text="☑️ Заказ Готов",
                    callback_data=EditOrderStatusCallback(status="active").pack()
                ),
                InlineKeyboardButton(
                    text="🚫 Заказ Не готов",
                    callback_data=EditOrderStatusCallback(status="passive").pack()
                ),
            ],
            [
                InlineKeyboardButton(
                    text="💤 Заказ выполнен",
                    callback_data=EditOrderStatusCallback(status="deactivate").pack()
                ),
            ]
        ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard


def get_keyboard_fab():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="☑️ Заказ Готов", callback_data=EditOrderStatusCallback(status="activate")
    )
    builder.button(
        text="-1", callback_data=EditOrderStatusCallback(status="passive")
    )
    builder.button(
        text="+1", callback_data=EditOrderStatusCallback(status="deactivate")
    )

    # Выравниваем кнопки по 4 в ряд, чтобы получилось 4 + 1
    builder.adjust(4)
    return builder.as_markup()