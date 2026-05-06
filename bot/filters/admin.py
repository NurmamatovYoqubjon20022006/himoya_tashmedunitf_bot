"""IsAdmin filter."""
from __future__ import annotations

from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message

from config import settings


class IsAdmin(Filter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        if not event.from_user:
            return False
        return event.from_user.id in settings.admin_ids
