"""Murojaat yuborish — 3 bosqichli oqim (progress + back tugmasi)."""
from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import IncidentType
from bot.database.queries import create_report, get_or_create_user
from bot.keyboards.main import (
    back_cancel_kb,
    confirm_kb,
    incident_type_kb,
    main_menu,
)
from bot.states.report import ReportSG
from bot.utils.i18n import t
from config import settings

router = Router(name="report")


REPORT_TRIGGERS = {
    "📝 Murojaat yuborish",
    "📝 Отправить обращение",
    "📝 Submit report",
    # eski tugmalar bilan ham ishlasin (back-compat)
    "🆘 Anonim murojaat yuborish",
    "🆘 Анонимное обращение",
    "🆘 Anonymous report",
}
CANCEL_TEXTS = {"❌ Bekor qilish", "❌ Отмена", "❌ Cancel"}
BACK_TEXTS = {"⬅️ Orqaga", "⬅️ Назад", "⬅️ Back"}


# ===================== START =====================


@router.message(F.text.in_(REPORT_TRIGGERS))
async def report_start(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    user = await get_or_create_user(session, message.from_user.id)
    if not user.is_registered:
        await message.answer(t("common.not_registered", user.language))
        return
    await state.clear()
    await _show_step_1(message, state, user.language, user.full_name or "")


# ===================== [1/3] HODISA TURI =====================


async def _show_step_1(
    message: Message, state: FSMContext, lang: str, name: str
) -> None:
    await state.set_state(ReportSG.incident_type)
    await message.answer(
        t("report.intro", lang, name=name),
        reply_markup=incident_type_kb(lang),
        parse_mode="HTML",
    )


@router.callback_query(ReportSG.incident_type, F.data.startswith("incident:"))
async def on_incident_type(
    call: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    user = await get_or_create_user(session, call.from_user.id)
    incident = call.data.split(":", 1)[1]
    incident_label = t(f"report.type.{incident}", user.language)

    await state.update_data(incident_type=incident)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer(t("report.feedback_type", user.language))
    await _show_step_2(call.message, state, user.language)


# ===================== [2/3] TAFSILOT =====================


async def _show_step_2(
    message: Message, state: FSMContext, lang: str
) -> None:
    await state.set_state(ReportSG.description)
    await message.answer(
        t("report.ask_description", lang),
        reply_markup=back_cancel_kb(lang),
        parse_mode="HTML",
    )


@router.message(ReportSG.description, F.text)
async def on_description(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    user = await get_or_create_user(session, message.from_user.id)

    if message.text in CANCEL_TEXTS:
        await _cancel(message, state, user.language)
        return

    if message.text in BACK_TEXTS:
        # ⬅️ Orqaga: 1-bosqichga
        await _show_step_1(message, state, user.language, user.full_name or "")
        return

    text = message.text.strip()
    if len(text) < 20:
        await message.answer(
            t("report.too_short", user.language, count=len(text))
        )
        return

    await state.update_data(description=text)
    await message.answer(
        t("report.feedback_description", user.language),
        parse_mode="HTML",
    )
    await _show_step_3(message, state, user.language, user)


# ===================== [3/3] TASDIQLASH =====================


async def _show_step_3(
    message: Message, state: FSMContext, lang: str, user
) -> None:
    data = await state.get_data()
    incident_label = t(f"report.type.{data['incident_type']}", lang)
    text = t(
        "report.confirm",
        lang,
        type=incident_label,
        description=data["description"],
        full_name=user.full_name or "—",
        phone=user.phone or "—",
    )
    await state.set_state(ReportSG.confirm)
    await message.answer(
        text,
        reply_markup=confirm_kb(lang),
        parse_mode="HTML",
    )


@router.callback_query(ReportSG.confirm, F.data == "confirm:back")
async def on_confirm_back(
    call: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    """⬅️ Orqaga — tafsilotni qayta yozish (2-bosqich)."""
    user = await get_or_create_user(session, call.from_user.id)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer(t("report.back_done", user.language))
    await _show_step_2(call.message, state, user.language)


@router.callback_query(ReportSG.confirm, F.data == "confirm:cancel")
async def on_confirm_cancel(
    call: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    user = await get_or_create_user(session, call.from_user.id)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        t("report.cancelled", user.language),
        reply_markup=main_menu(user.language),
    )
    await state.clear()
    await call.answer()


@router.callback_query(ReportSG.confirm, F.data == "confirm:send")
async def on_confirm_send(
    call: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
) -> None:
    user = await get_or_create_user(session, call.from_user.id)
    data = await state.get_data()
    try:
        report = await create_report(
            session,
            user_id=user.id,
            incident_type=IncidentType(data["incident_type"]),
            description=data["description"],
            location=None,
            incident_date=None,
            is_anonymous=False,
        )
    except Exception:
        logger.exception("Failed to create report")
        await call.message.answer(t("common.error", user.language))
        await state.clear()
        await call.answer()
        return

    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        t("report.success", user.language, tracking_id=report.tracking_id),
        reply_markup=main_menu(user.language),
        parse_mode="HTML",
    )
    await state.clear()
    await call.answer("✅")
    await _notify_admins(bot, report.tracking_id, data, user)


# ===================== HELPERS =====================


async def _cancel(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    await message.answer(
        t("report.cancelled", lang), reply_markup=main_menu(lang)
    )


async def _notify_admins(
    bot: Bot, tracking_id: str, data: dict, user
) -> None:
    if not settings.admin_ids:
        return
    user_info = (
        f"<b>F.I.O:</b> {user.full_name or '—'}\n"
        f"<b>Telefon:</b> <code>{user.phone or '—'}</code>\n"
    )
    if user.faculty:
        user_info += f"<b>Fakultet:</b> {user.faculty.value}\n"
    if user.course:
        user_info += f"<b>Kurs:</b> {user.course}\n"
    if user.direction:
        user_info += f"<b>Yo'nalish:</b> {user.direction}\n"
    if user.group_name:
        user_info += f"<b>Guruh:</b> {user.group_name}\n"
    if user.position:
        user_info += f"<b>Lavozim:</b> {user.position}\n"

    text = (
        f"🆕 <b>Yangi murojaat</b>\n\n"
        f"<b>ID:</b> <code>{tracking_id}</code>\n"
        f"<b>Turi:</b> {data['incident_type']}\n\n"
        f"👤 <b>Murojaatchi:</b>\n{user_info}\n"
        f"<b>Tafsilot:</b>\n{data['description']}"
    )
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(admin_id, text, parse_mode="HTML")
        except Exception:
            logger.exception(f"Failed to notify admin {admin_id}")
