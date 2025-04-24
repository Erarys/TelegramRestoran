from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData

class OrderCallback(CallbackData, prefix="order"):
    table_id: int

class FoodCallback(CallbackData, prefix="food"):
    food: str

class FoodCountCallback(CallbackData, prefix="food_count"):
    action: str


def order_callback() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="0️⃣",
                callback_data=OrderCallback(table_id=0).pack()
            ),
            InlineKeyboardButton(
                text="1️⃣",
                callback_data=OrderCallback(table_id=1).pack()
            ),
        ],
        [
            InlineKeyboardButton(
                text="2️⃣",
                callback_data=OrderCallback(table_id=2).pack()
            ),
            InlineKeyboardButton(
                text="3️⃣",
                callback_data=OrderCallback(table_id=3).pack()
            ),
        ],
        [
            InlineKeyboardButton(
                text="4️⃣",
                callback_data=OrderCallback(table_id=4).pack()
            ),
            InlineKeyboardButton(
                text="5️⃣",
                callback_data=OrderCallback(table_id=5).pack()
            ),
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def food_callback() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="Шашлыки",
                callback_data=FoodCallback(food="Шашлык").pack()
            ),
            InlineKeyboardButton(
                text="Напитки",
                callback_data=FoodCallback(food="Напитки").pack()
            ),
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def count_food() -> InlineKeyboardMarkup:
    buttons =  [
        [
            InlineKeyboardButton(
                text="-1",
                callback_data=FoodCountCallback(action="decr").pack()
            ),
            InlineKeyboardButton(
                text="+1",
                callback_data=FoodCountCallback(action="incr").pack()
            ),
        ],
        [
            InlineKeyboardButton(
                text="Подтвердить",
                callback_data=FoodCountCallback(action="finish").pack()
            ),
        ]


    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
