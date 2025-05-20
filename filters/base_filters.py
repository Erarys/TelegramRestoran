from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message


class ChatTypeFilter(BaseFilter):  # [1]
    def __init__(self, chat_type: Union[str, list]):  # [2]
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:  # [3]
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type


class IsCook(BaseFilter):
    async def __call__(self, message: Message):
        print(message.from_user.id)
        if message.from_user.id == 1833531133:
            return True
        await message.answer("Недостаточно прав доступа")


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message):
        print(message.from_user.id)
        if message.from_user.id == 1833531133:
            return True
        await message.answer("Недостаточно прав доступа")