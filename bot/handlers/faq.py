"""FAQ va kontaktlar."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.queries import get_or_create_user
from bot.utils.i18n import t

router = Router(name="faq")


FAQ_TRIGGERS = {"📖 Huquqlar va FAQ", "📖 Права и FAQ", "📖 Rights & FAQ"}
CONTACT_TRIGGERS = {
    "📞 Ishonch telefonlari",
    "📞 Телефоны доверия",
    "📞 Hotlines",
}


@router.message(F.text.in_(FAQ_TRIGGERS))
async def show_faq(message: Message, session: AsyncSession) -> None:
    user = await get_or_create_user(session, message.from_user.id)
    await message.answer(t("faq.title", user.language), parse_mode="HTML")


@router.message(F.text.in_(CONTACT_TRIGGERS))
async def show_contacts(message: Message, session: AsyncSession) -> None:
    user = await get_or_create_user(session, message.from_user.id)
    await message.answer(t("contacts.title", user.language), parse_mode="HTML")
