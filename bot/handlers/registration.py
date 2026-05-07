"""Foydalanuvchi ro'yxatdan o'tish oqimi."""
from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
    ReplyKeyboardRemove,
)
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Faculty, UserType
from bot.database.queries import (
    get_or_create_user,
    is_phone_taken,
    register_user,
)
from bot.keyboards.main import main_menu
from bot.keyboards.registration import (
    FACULTY_LABELS,
    cancel_only_kb,
    confirm_registration_kb,
    contact_kb,
    course_kb,
    faculty_kb,
    skip_or_cancel_kb,
    user_type_kb,
)
from bot.states.registration import RegistrationSG
from bot.utils.i18n import t

router = Router(name="registration")


PHONE_RE = re.compile(r"^\+?\d{9,15}$")
# F.I.O — har bir bo'lak: harflar (lotin/kirill/o'zbek), apostrof yoki defis bilan
FIO_PART_RE = re.compile(r"^[A-Za-zА-Яа-яЁёЎўҚқҒғҲҳ'ʻʼ\-]{2,}$")
CANCEL_TEXTS = {"❌ Bekor qilish", "❌ Отмена", "❌ Cancel"}
SKIP_TEXTS = {"⏭️ O'tkazib yuborish", "⏭️ Пропустить", "⏭️ Skip"}


def _validate_fio(raw: str) -> str | None:
    """F.I.O ni tekshirish: kamida 3 ta bo'lak, har biri faqat harflardan.

    To'g'ri bo'lsa — bo'sh joylarni siqib qaytaradi (foydalanuvchi
    yozganidek). Noto'g'ri bo'lsa — None.
    """
    parts = raw.split()
    if len(parts) < 3:
        return None
    for p in parts:
        if not FIO_PART_RE.match(p):
            return None
    return " ".join(parts)


def _user_type_label(t_val: UserType, lang: str) -> str:
    return t(f"ut.{t_val.value}", lang)


def _faculty_label(f: Faculty, lang: str) -> str:
    return t(f"fac.{f.value}", lang)


def _normalize_phone(raw: str) -> str | None:
    """+998901234567 → +998901234567. Faqat raqam va '+' qoldiramiz."""
    cleaned = re.sub(r"[^\d+]", "", raw)
    if not cleaned:
        return None
    if not cleaned.startswith("+"):
        cleaned = "+" + cleaned
    if not PHONE_RE.match(cleaned):
        return None
    return cleaned


# ===================== START =====================


@router.message(Command("register"))
async def cmd_register(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    user = await get_or_create_user(
        session, message.from_user.id, username=message.from_user.username
    )
    await _start_registration(message, state, user.language)


async def _start_registration(
    message: Message, state: FSMContext, lang: str
) -> None:
    await state.clear()
    await state.set_state(RegistrationSG.waiting_phone)
    await message.answer(t("reg.start", lang), parse_mode="HTML")
    await message.answer(
        t("reg.share_contact", lang) + " ⬇️",
        reply_markup=contact_kb(lang),
    )


# ===================== 1. PHONE =====================


@router.message(RegistrationSG.waiting_phone, F.contact)
async def reg_phone_contact(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    user = await get_or_create_user(session, message.from_user.id)

    if message.contact.user_id and message.contact.user_id != message.from_user.id:
        await message.answer(
            "❗ Faqat o'z raqamingizni yuboring.",
            reply_markup=contact_kb(user.language),
        )
        return

    phone = _normalize_phone(message.contact.phone_number)
    if not phone:
        await message.answer(
            t("reg.phone_invalid", user.language),
            reply_markup=contact_kb(user.language),
        )
        return

    if await is_phone_taken(session, phone, exclude_telegram_id=user.telegram_id):
        await message.answer(
            t("reg.phone_taken", user.language),
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.clear()
        return

    await state.update_data(phone=phone)
    await state.set_state(RegistrationSG.waiting_full_name)
    await message.answer(
        t("reg.ask_full_name", user.language, phone=phone),
        reply_markup=cancel_only_kb(user.language),
        parse_mode="HTML",
    )


@router.message(RegistrationSG.waiting_phone, F.text)
async def reg_phone_text(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    user = await get_or_create_user(session, message.from_user.id)
    if message.text in CANCEL_TEXTS:
        await _cancel(message, state, user.language)
        return
    await message.answer(
        t("reg.phone_invalid", user.language),
        reply_markup=contact_kb(user.language),
    )


# ===================== 2. FULL NAME =====================


@router.message(RegistrationSG.waiting_full_name, F.text)
async def reg_full_name(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    user = await get_or_create_user(session, message.from_user.id)
    if message.text in CANCEL_TEXTS:
        await _cancel(message, state, user.language)
        return

    name = _validate_fio(message.text.strip())
    if name is None:
        await message.answer(
            t("reg.name_invalid", user.language), parse_mode="HTML"
        )
        return

    await state.update_data(full_name=name)
    await state.set_state(RegistrationSG.waiting_user_type)
    await message.answer(
        t("reg.ask_user_type", user.language, name=name),
        reply_markup=user_type_kb(user.language),
        parse_mode="HTML",
    )


# ===================== 3. USER TYPE =====================


@router.callback_query(
    RegistrationSG.waiting_user_type, F.data.startswith("reg_type:")
)
async def reg_user_type(
    call: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    user = await get_or_create_user(session, call.from_user.id)
    type_val = call.data.split(":", 1)[1]
    try:
        user_type = UserType(type_val)
    except ValueError:
        await call.answer("Noto'g'ri qiymat")
        return

    await state.update_data(user_type=user_type.value)
    await call.message.edit_reply_markup(reply_markup=None)

    if user_type in (UserType.STUDENT, UserType.MASTER):
        await state.set_state(RegistrationSG.waiting_faculty)
        await call.message.answer(
            t("reg.ask_faculty", user.language),
            reply_markup=faculty_kb(),
            parse_mode="HTML",
        )
    elif user_type == UserType.TEACHER:
        await state.set_state(RegistrationSG.waiting_faculty)
        await call.message.answer(
            t("reg.ask_faculty", user.language),
            reply_markup=faculty_kb(),
            parse_mode="HTML",
        )
    else:
        # staff / other → to'g'ridan-to'g'ri lavozim so'raladi
        await state.set_state(RegistrationSG.waiting_position)
        await call.message.answer(
            t("reg.ask_position", user.language),
            reply_markup=skip_or_cancel_kb(user.language),
            parse_mode="HTML",
        )

    await call.answer()


# ===================== 4. FACULTY =====================


@router.callback_query(
    RegistrationSG.waiting_faculty, F.data.startswith("reg_fac:")
)
async def reg_faculty(
    call: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    user = await get_or_create_user(session, call.from_user.id)
    fac_val = call.data.split(":", 1)[1]
    try:
        faculty = Faculty(fac_val)
    except ValueError:
        await call.answer("Noto'g'ri fakultet")
        return

    await state.update_data(faculty=faculty.value)
    await call.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    user_type = UserType(data["user_type"])

    if user_type == UserType.TEACHER:
        # O'qituvchi: lavozim so'raladi
        await state.set_state(RegistrationSG.waiting_position)
        await call.message.answer(
            t("reg.ask_position", user.language),
            reply_markup=skip_or_cancel_kb(user.language),
            parse_mode="HTML",
        )
    else:
        # Talaba/magistr: kurs so'raladi
        await state.set_state(RegistrationSG.waiting_course)
        await call.message.answer(
            t("reg.ask_course", user.language),
            reply_markup=course_kb(),
            parse_mode="HTML",
        )

    await call.answer()


# ===================== 5. COURSE =====================


@router.callback_query(
    RegistrationSG.waiting_course, F.data.startswith("reg_course:")
)
async def reg_course(
    call: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    user = await get_or_create_user(session, call.from_user.id)
    try:
        course = int(call.data.split(":", 1)[1])
    except ValueError:
        await call.answer("Noto'g'ri kurs")
        return

    if not (1 <= course <= 7):
        await call.answer("Kurs 1-7 oralig'ida bo'lishi kerak")
        return

    await state.update_data(course=course)
    await call.message.edit_reply_markup(reply_markup=None)
    await state.set_state(RegistrationSG.waiting_direction)
    await call.message.answer(
        t("reg.ask_direction", user.language),
        reply_markup=cancel_only_kb(user.language),
        parse_mode="HTML",
    )
    await call.answer()


# ===================== 6. DIRECTION (free text) =====================


@router.message(RegistrationSG.waiting_direction, F.text)
async def reg_direction(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    user = await get_or_create_user(session, message.from_user.id)
    if message.text in CANCEL_TEXTS:
        await _cancel(message, state, user.language)
        return

    direction = message.text.strip()
    if len(direction) < 3:
        await message.answer(t("reg.direction_too_short", user.language))
        return

    await state.update_data(direction=direction)
    await state.set_state(RegistrationSG.waiting_group)
    await message.answer(
        t("reg.ask_group", user.language),
        reply_markup=skip_or_cancel_kb(user.language),
        parse_mode="HTML",
    )


# ===================== 7. GROUP (optional) =====================


@router.message(RegistrationSG.waiting_group, F.text)
async def reg_group(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    user = await get_or_create_user(session, message.from_user.id)
    if message.text in CANCEL_TEXTS:
        await _cancel(message, state, user.language)
        return

    group = None if message.text in SKIP_TEXTS else message.text.strip()[:64]
    await state.update_data(group_name=group)
    await _show_confirm(message, state, user.language)


# ===================== 8. POSITION (teacher/staff/other) =====================


@router.message(RegistrationSG.waiting_position, F.text)
async def reg_position(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    user = await get_or_create_user(session, message.from_user.id)
    if message.text in CANCEL_TEXTS:
        await _cancel(message, state, user.language)
        return

    position = None if message.text in SKIP_TEXTS else message.text.strip()[:255]
    await state.update_data(position=position)
    await _show_confirm(message, state, user.language)


# ===================== 9. CONFIRM =====================


async def _show_confirm(
    message: Message, state: FSMContext, lang: str
) -> None:
    data = await state.get_data()
    user_type = UserType(data["user_type"])

    extras: list[str] = []
    if data.get("faculty"):
        extras.append(t("profile.faculty", lang, faculty=_faculty_label(Faculty(data["faculty"]), lang)))
    if data.get("course"):
        extras.append(t("profile.course", lang, course=data["course"]))
    if data.get("direction"):
        extras.append(t("profile.direction", lang, direction=data["direction"]))
    if data.get("group_name"):
        extras.append(t("profile.group", lang, group=data["group_name"]))
    if data.get("position"):
        extras.append(t("profile.position", lang, position=data["position"]))

    extra_text = "\n".join(extras) + ("\n\n" if extras else "")

    text = t(
        "reg.confirm_title",
        lang,
        full_name=data["full_name"],
        phone=data["phone"],
        user_type=_user_type_label(user_type, lang),
        extra=extra_text,
    )
    await state.set_state(RegistrationSG.waiting_confirm)
    await message.answer(
        text,
        reply_markup=confirm_registration_kb(lang),
        parse_mode="HTML",
    )


@router.callback_query(
    RegistrationSG.waiting_confirm, F.data == "reg_confirm:yes"
)
async def reg_confirm_yes(
    call: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    user = await get_or_create_user(session, call.from_user.id)
    data = await state.get_data()

    try:
        registered = await register_user(
            session,
            telegram_id=call.from_user.id,
            phone=data["phone"],
            full_name=data["full_name"],
            user_type=UserType(data["user_type"]),
            faculty=Faculty(data["faculty"]) if data.get("faculty") else None,
            course=data.get("course"),
            direction=data.get("direction"),
            group_name=data.get("group_name"),
            position=data.get("position"),
        )
    except Exception:
        logger.exception("Registratsiya xatolik")
        await call.message.answer(t("common.error", user.language))
        await state.clear()
        await call.answer()
        return

    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        t("reg.success", user.language, name=registered.full_name),
        reply_markup=main_menu(user.language),
        parse_mode="HTML",
    )
    await state.clear()
    await call.answer("✅")
    logger.info(
        f"Yangi foydalanuvchi: {registered.full_name} | "
        f"{registered.phone} | {registered.user_type}"
    )


@router.callback_query(
    RegistrationSG.waiting_confirm, F.data == "reg_confirm:restart"
)
async def reg_confirm_restart(
    call: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    user = await get_or_create_user(session, call.from_user.id)
    await call.message.edit_reply_markup(reply_markup=None)
    await _start_registration(call.message, state, user.language)
    await call.answer()


# ===================== CANCEL =====================


async def _cancel(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    await message.answer(
        t("reg.cancelled", lang), reply_markup=ReplyKeyboardRemove()
    )
