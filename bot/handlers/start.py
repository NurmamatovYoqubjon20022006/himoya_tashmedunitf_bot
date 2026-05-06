"""/start, /help, /profile, til tanlash, mening murojaatlarim."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Faculty, UserType
from bot.database.queries import (
    _invalidate_cache,
    get_or_create_user,
    list_user_reports,
    set_user_language,
)
from bot.handlers.registration import _start_registration
from bot.keyboards.main import language_kb, main_menu
from bot.utils.i18n import t

router = Router(name="start")


# Yorliqlar — admin handler'larida ishlatilgan o'sha lug'atlardan foydalanamiz
INCIDENT_LABELS_MAP: dict[str, str] = {
    "harassment": "Shilqimlik",
    "pressure": "Tazyiq",
    "violence": "Zo'ravonlik",
    "discrimination": "Kamsitish",
    "other": "Boshqa",
}

STATUS_LABELS_MAP: dict[str, str] = {
    "new": "🆕 Yangi",
    "in_review": "🔍 Ko'rib chiqilmoqda",
    "resolved": "✅ Hal qilingan",
    "rejected": "❌ Rad etilgan",
}


def _user_type_label(user_type: UserType, lang: str) -> str:
    return t(f"ut.{user_type.value}", lang)


def _faculty_label(faculty: Faculty, lang: str) -> str:
    return t(f"fac.{faculty.value}", lang)


@router.message(CommandStart())
async def cmd_start(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    await state.clear()
    # Cache'ni majburan tozalaymiz — DB'da o'zgarishlar bo'lgan bo'lishi mumkin
    _invalidate_cache(message.from_user.id)

    user = await get_or_create_user(
        session,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
    )

    if not user.is_registered:
        # Salomlashish + registratsiya
        await message.answer(t("start.welcome", user.language), parse_mode="HTML")
        await message.answer(
            t("start.need_register", user.language), parse_mode="HTML"
        )
        await _start_registration(message, state, user.language)
        return

    # Ro'yxatdan o'tgan foydalanuvchi — asosiy menyu
    await message.answer(
        t("start.welcome_back", user.language, name=user.full_name or "do'stim"),
        reply_markup=main_menu(user.language),
        parse_mode="HTML",
    )


@router.message(Command("language"))
@router.message(F.text.in_({"🌐 Tilni o'zgartirish", "🌐 Сменить язык", "🌐 Change language"}))
async def cmd_language(message: Message) -> None:
    await message.answer(
        t("lang.choose"),
        reply_markup=language_kb(),
    )


@router.callback_query(F.data.startswith("lang:"))
async def set_lang(
    call: CallbackQuery, session: AsyncSession
) -> None:
    lang = call.data.split(":", 1)[1]
    await set_user_language(session, call.from_user.id, lang)
    await call.message.edit_text(t("lang.set", lang))
    user = await get_or_create_user(session, call.from_user.id)
    if user.is_registered:
        await call.message.answer(
            t("start.welcome_back", lang, name=user.full_name or ""),
            reply_markup=main_menu(lang),
            parse_mode="HTML",
        )
    else:
        await call.message.answer(t("start.need_register", lang), parse_mode="HTML")
    await call.answer()


@router.message(Command("help"))
async def cmd_help(message: Message, session: AsyncSession) -> None:
    user = await get_or_create_user(session, message.from_user.id)
    await message.answer(t("start.welcome", user.language), parse_mode="HTML")


@router.message(Command("cancel"))
async def cmd_cancel(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    user = await get_or_create_user(session, message.from_user.id)
    await state.clear()
    kb = main_menu(user.language) if user.is_registered else None
    await message.answer(t("common.cancelled", user.language), reply_markup=kb)


# ===================== PROFILE =====================


PROFILE_TRIGGERS = {"👤 Profilim", "👤 Профиль", "👤 My profile"}


@router.message(Command("profile"))
@router.message(F.text.in_(PROFILE_TRIGGERS))
async def cmd_profile(message: Message, session: AsyncSession) -> None:
    user = await get_or_create_user(session, message.from_user.id)
    if not user.is_registered:
        await message.answer(t("common.not_registered", user.language))
        return

    extras: list[str] = []
    if user.faculty:
        extras.append(
            t("profile.faculty", user.language, faculty=_faculty_label(user.faculty, user.language))
        )
    if user.course:
        extras.append(t("profile.course", user.language, course=user.course))
    if user.direction:
        extras.append(t("profile.direction", user.language, direction=user.direction))
    if user.group_name:
        extras.append(t("profile.group", user.language, group=user.group_name))
    if user.position:
        extras.append(t("profile.position", user.language, position=user.position))

    extra_text = "\n".join(extras) + ("\n\n" if extras else "")
    registered_at = (
        user.registered_at.strftime("%Y-%m-%d") if user.registered_at else "—"
    )

    text = t(
        "profile.title",
        user.language,
        phone=user.phone or "—",
        full_name=user.full_name or "—",
        user_type=_user_type_label(user.user_type, user.language) if user.user_type else "—",
        extra=extra_text,
        registered_at=registered_at,
    )
    await message.answer(
        text, reply_markup=main_menu(user.language), parse_mode="HTML"
    )


# ===================== MY REPORTS =====================


MY_REPORTS_TRIGGERS = {
    "📋 Mening murojaatlarim",
    "📋 Мои обращения",
    "📋 My reports",
}


@router.message(Command("my_reports"))
@router.message(F.text.in_(MY_REPORTS_TRIGGERS))
async def cmd_my_reports(message: Message, session: AsyncSession) -> None:
    user = await get_or_create_user(session, message.from_user.id)
    if not user.is_registered:
        await message.answer(t("common.not_registered", user.language))
        return

    reports = await list_user_reports(session, user.id, limit=20)
    if not reports:
        await message.answer(
            t("my_reports.empty", user.language),
            reply_markup=main_menu(user.language),
        )
        return

    lines = [t("my_reports.title", user.language, total=len(reports)), ""]
    for r in reports:
        lines.append(
            t(
                "my_reports.item",
                user.language,
                tracking_id=r.tracking_id,
                date=r.created_at.strftime("%Y-%m-%d %H:%M"),
                type=INCIDENT_LABELS_MAP.get(r.incident_type.value, r.incident_type.value),
                status=STATUS_LABELS_MAP.get(r.status.value, r.status.value),
            )
        )

    await message.answer(
        "\n".join(lines),
        reply_markup=main_menu(user.language),
        parse_mode="HTML",
    )
