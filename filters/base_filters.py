from typing import Union, List

from aiogram.filters import BaseFilter
from aiogram.types import Message

import os, json


class ChatTypeFilter(BaseFilter):  # [1]
    def __init__(self, chat_type: Union[str, list]):  # [2]
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:  # [3]
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type


class IsCook(BaseFilter):
    def __init__(self):
        self.user_ids: List[int] = json.loads(os.getenv("COOK_LS", "[]"))

    async def __call__(self, message: Message):
        if message.from_user.id in self.user_ids:
            return True
        await message.answer(f"Недостаточно прав доступа {message.from_user.id}")
        return False


class IsWaiter(BaseFilter):
    def __init__(self):
        self.user_ids: List[int] = json.loads(os.getenv("WAITER_LS", "[]"))

    async def __call__(self, message: Message):
        if message.from_user.id in self.user_ids:
            return True
        await message.answer(f"Недостаточно прав доступа {message.from_user.id}")
        return False


class IsAdmin(BaseFilter):
    def __init__(self):
        self.user_ids: List[int] = json.loads(os.getenv("ADMIN_LS", "[]"))

    async def __call__(self, message: Message):
        if message.from_user.id in self.user_ids:
            return True
        await message.answer(f"Недостаточно прав доступа {message.from_user.id}")
        return False
