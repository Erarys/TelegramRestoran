import re
from contextlib import suppress

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboards.order_keyboard import EditOrderStatusCallback, ready_order

router = Router()

@router.callback_query(EditOrderStatusCallback.filter())
async def edit_order_status(callback: CallbackQuery, callback_data: EditOrderStatusCallback, state: FSMContext):
    old_text = callback.message.text

    with suppress(TelegramBadRequest):
        if callback_data.status == "Готов":
            await callback.message.bot.send_message(
                1833531133,
                text=old_text
            )

        new_text = re.sub(r'Статус заказа: .*$', f'Статус заказа: {callback_data.status}', old_text)
        await callback.message.edit_text(new_text, reply_markup=ready_order())
        await callback.answer()
