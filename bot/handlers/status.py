"""Murojaat holatini tekshirish."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.queries import get_or_create_user, get_report_by_tracking_id
from bot.keyboards.main import cancel_kb, main_menu
from bot.states.report import StatusSG
from bot.utils.i18n import t

router = Router(name="status")


STATUS_TRIGGERS = {
    "📋 Murojaat holatini tekshirish",
    "📋 Проверить статус",
    "📋 Check status",
}
CANCEL_TEXTS = {"❌ Bekor qilish", "❌ Отмена", "❌ Cancel"}


@router.message(F.text.in_(STATUS_TRIGGERS))
async def status_start(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    user = await get_or_create_user(session, message.from_user.id)
    await state.set_state(StatusSG.waiting_id)
    await message.answer(
        t("status.ask_id", user.language),
        reply_markup=cancel_kb(user.language),
    )


@router.message(StatusSG.waiting_id, F.text)
async def status_lookup(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    user = await get_or_create_user(session, message.from_user.id)
    if message.text in CANCEL_TEXTS:
        await state.clear()
        await message.answer(
            t("common.cancelled", user.language),
            reply_markup=main_menu(user.language),
        )
        return

    tracking_id = message.text.strip().upper()
    report = await get_report_by_tracking_id(session, tracking_id)

    if report is None:
        await message.answer(t("status.not_found", user.language))
        return

    status_label = t(f"status.{report.status.value}", user.language)
    note = (
        t("status.note", user.language, note=report.admin_note)
        if report.admin_note
        else ""
    )
    text = t(
        "status.info",
        user.language,
        tracking_id=report.tracking_id,
        status=status_label,
        created=report.created_at.strftime("%Y-%m-%d %H:%M"),
        updated=report.updated_at.strftime("%Y-%m-%d %H:%M"),
        note=note,
    )
    await state.clear()
    await message.answer(
        text, reply_markup=main_menu(user.language), parse_mode="HTML"
    )
