from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

class FoodDeleteCallback(CallbackData, prefix="menu"):
    food_id: int

def get_menu_button(food_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="Удалить 🗑",
                callback_data=FoodDeleteCallback(food_id=food_id).pack()
            )
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard