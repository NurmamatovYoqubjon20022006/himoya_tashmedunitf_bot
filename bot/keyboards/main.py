"""Reply va inline klaviaturalar."""
from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from bot.utils.i18n import t


def main_menu(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("menu.report", lang))],
            [
                KeyboardButton(text=t("menu.my_reports", lang)),
                KeyboardButton(text=t("menu.profile", lang)),
            ],
            [
                KeyboardButton(text=t("menu.faq", lang)),
                KeyboardButton(text=t("menu.contacts", lang)),
            ],
            [KeyboardButton(text=t("menu.language", lang))],
        ],
        resize_keyboard=True,
    )


def cancel_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("menu.cancel", lang))]],
        resize_keyboard=True,
    )


def back_cancel_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """⬅️ Orqaga + ❌ Bekor qilish."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t("menu.back", lang)),
                KeyboardButton(text=t("menu.cancel", lang)),
            ],
        ],
        resize_keyboard=True,
    )


def skip_cancel_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("menu.skip", lang))],
            [KeyboardButton(text=t("menu.cancel", lang))],
        ],
        resize_keyboard=True,
    )


def done_skip_cancel_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("menu.done", lang))],
            [KeyboardButton(text=t("menu.cancel", lang))],
        ],
        resize_keyboard=True,
    )


def language_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
            ]
        ]
    )


def incident_type_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("report.type.harassment", lang),
                    callback_data="incident:harassment",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("report.type.pressure", lang),
                    callback_data="incident:pressure",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("report.type.violence", lang),
                    callback_data="incident:violence",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("report.type.discrimination", lang),
                    callback_data="incident:discrimination",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("report.type.other", lang),
                    callback_data="incident:other",
                )
            ],
        ]
    )


def confirm_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("report.confirm.send", lang), callback_data="confirm:send"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("menu.back", lang), callback_data="confirm:back"
                ),
                InlineKeyboardButton(
                    text=t("menu.cancel", lang), callback_data="confirm:cancel"
                ),
            ],
        ]
    )
