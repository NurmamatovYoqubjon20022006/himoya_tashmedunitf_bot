"""Registratsiya klaviaturalari."""
from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from bot.database.models import Faculty, UserType
from bot.utils.i18n import t


# Fakultet ko'rsatish nomlari (i18n key emas — qisqa yorliqlar)
FACULTY_LABELS: dict[Faculty, str] = {
    Faculty.DAVOLASH_1: "🩺 1-son Davolash fakulteti",
    Faculty.DAVOLASH_2: "🏥 2-son Davolash fakulteti",
    Faculty.PEDIATRIYA: "👶 Pediatriya fakulteti",
    Faculty.XALQARO: "🌍 Xalqaro ta'lim fakulteti",
}


def contact_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Telefon raqamini Telegram orqali yuborish."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=t("reg.share_contact", lang),
                    request_contact=True,
                )
            ],
            [KeyboardButton(text=t("menu.cancel", lang))],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def user_type_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Foydalanuvchi maqomini tanlash."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("reg.type.student", lang),
                    callback_data="reg_type:student",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("reg.type.master", lang),
                    callback_data="reg_type:master",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("reg.type.teacher", lang),
                    callback_data="reg_type:teacher",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("reg.type.staff", lang),
                    callback_data="reg_type:staff",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("reg.type.other", lang),
                    callback_data="reg_type:other",
                )
            ],
        ]
    )


def faculty_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data=f"reg_fac:{f.value}")]
            for f, label in FACULTY_LABELS.items()
        ]
    )


def course_kb() -> InlineKeyboardMarkup:
    """1-7 kurs."""
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text=str(c), callback_data=f"reg_course:{c}")
            for c in (1, 2, 3, 4)
        ],
        [
            InlineKeyboardButton(text=str(c), callback_data=f"reg_course:{c}")
            for c in (5, 6, 7)
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_registration_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("reg.confirm.send", lang),
                    callback_data="reg_confirm:yes",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("reg.confirm.restart", lang),
                    callback_data="reg_confirm:restart",
                )
            ],
        ]
    )


def cancel_only_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("menu.cancel", lang))]],
        resize_keyboard=True,
    )


def skip_or_cancel_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("menu.skip", lang))],
            [KeyboardButton(text=t("menu.cancel", lang))],
        ],
        resize_keyboard=True,
    )
