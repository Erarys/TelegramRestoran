from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


class TableCallback(CallbackData, prefix="table"):
    action: str
    table_id: str


class EditOrderStatusCallback(CallbackData, prefix="edit_status"):
    status: str
    order_creator_id: int


def get_table_button(amount: int):
    builder = ReplyKeyboardBuilder()

    for i in range(1, amount + 1):
        builder.add(KeyboardButton(text=str(i)))

    builder.adjust(3)

    return builder.as_markup()


def get_order_button(menu):
    builder = ReplyKeyboardBuilder()


    for food in menu.values():
        builder.add(KeyboardButton(text=str(food["name"])))

    builder.add(KeyboardButton(text="/Отменить"))
    builder.add(KeyboardButton(text="Сохранить"))
    builder.adjust(3)
    return builder.as_markup()


def get_count_button():
    builder = ReplyKeyboardBuilder()

    for i in range(0, 9):
        builder.add(KeyboardButton(text=str(i)))

    builder.adjust(3)

    return builder.as_markup()


def get_order_option_button(table_id) -> InlineKeyboardButton:
    buttons = [
        [
            InlineKeyboardButton(
                text="🧹 Очистить стол",
                callback_data=TableCallback(action="clear", table_id=table_id).pack()
            ),
            InlineKeyboardButton(
                text="📝 Редактировать",
                callback_data=TableCallback(action="edit", table_id=table_id).pack()
            )
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard


def get_order_status_keyboard(order_creator_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="☑️ Заказ Готов",
        callback_data=EditOrderStatusCallback(status="Готов", order_creator_id=order_creator_id
                                              )
    )
    builder.button(
        text="🚫 Заказ Не готов",
        callback_data=EditOrderStatusCallback(status="Не готов", order_creator_id=order_creator_id
                                              )
    )
    builder.button(
        text="💤 Заказ выполнен",
        callback_data=EditOrderStatusCallback(status="Заказ выполнен", order_creator_id=order_creator_id
                                              )
    )

    # Выравниваем кнопки по 4 в ряд, чтобы получилось 4 + 1
    builder.adjust(4)
    return builder.as_markup()
