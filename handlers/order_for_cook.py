import re
from contextlib import suppress

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from filters.base_filters import IsCook
from keyboards.order_keyboard import EditOrderStatusCallback, get_order_status_keyboard

router = Router()


@router.callback_query(EditOrderStatusCallback.filter(), IsCook())
async def edit_order_status(callback: CallbackQuery, callback_data: EditOrderStatusCallback, state: FSMContext):
    used_text = callback.message.text

    text = re.sub(r"Статус заказа: .*$", f"Статус заказа: {callback_data.status}", used_text)
    await callback.message.edit_text(text, reply_markup=get_order_status_keyboard(callback_data.order_creator_id))
    await callback.answer()


    with suppress(TelegramBadRequest):
        if callback_data.status == "Готов":
            await callback.message.bot.send_message(
                callback_data.order_creator_id,
                text=text + f"\n<b>{callback.from_user.first_name}:</b> Прошу забрать заказ🚨🚨🚨"
            )
        elif callback_data.status == "Заказ выполнен":
            await callback.message.delete()
