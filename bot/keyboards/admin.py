"""Admin panel klaviaturalari."""
from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from bot.database.models import ReportStatus


def admin_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🆕 Yangi murojaatlar"), KeyboardButton(text="🔍 Ko'rib chiqilmoqda")],
            [KeyboardButton(text="✅ Hal qilingan"), KeyboardButton(text="❌ Rad etilgan")],
            [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="🔎 ID bo'yicha qidirish")],
            [KeyboardButton(text="📢 Broadcast"), KeyboardButton(text="🚪 Admin paneldan chiqish")],
        ],
        resize_keyboard=True,
    )


def reports_pagination(
    page: int,
    total_pages: int,
    status_filter: str = "all",
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    nav: list[InlineKeyboardButton] = []
    if page > 1:
        nav.append(
            InlineKeyboardButton(
                text="⬅️", callback_data=f"a:list:{status_filter}:{page - 1}"
            )
        )
    nav.append(
        InlineKeyboardButton(
            text=f"{page}/{total_pages}", callback_data="a:noop"
        )
    )
    if page < total_pages:
        nav.append(
            InlineKeyboardButton(
                text="➡️", callback_data=f"a:list:{status_filter}:{page + 1}"
            )
        )
    if nav:
        rows.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def report_actions(report_id: int, current_status: ReportStatus) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []

    status_buttons = []
    if current_status != ReportStatus.IN_REVIEW:
        status_buttons.append(
            InlineKeyboardButton(
                text="🔍 Ko'rib chiqilmoqda",
                callback_data=f"a:status:{report_id}:in_review",
            )
        )
    if current_status != ReportStatus.RESOLVED:
        status_buttons.append(
            InlineKeyboardButton(
                text="✅ Hal qilingan",
                callback_data=f"a:status:{report_id}:resolved",
            )
        )
    if current_status != ReportStatus.REJECTED:
        status_buttons.append(
            InlineKeyboardButton(
                text="❌ Rad etish",
                callback_data=f"a:status:{report_id}:rejected",
            )
        )

    for i in range(0, len(status_buttons), 1):
        rows.append([status_buttons[i]])

    rows.append(
        [
            InlineKeyboardButton(
                text="📝 Izoh qo'shish",
                callback_data=f"a:note:{report_id}",
            )
        ]
    )
    rows.append(
        [
            InlineKeyboardButton(
                text="📎 Fayllarni ko'rsatish",
                callback_data=f"a:files:{report_id}",
            )
        ]
    )
    rows.append(
        [
            InlineKeyboardButton(
                text="⬅️ Ro'yxatga qaytish",
                callback_data="a:list:all:1",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def cancel_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="a:cancel")]
        ]
    )


def confirm_broadcast() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Yuborish", callback_data="a:broadcast:send"),
                InlineKeyboardButton(text="❌ Bekor", callback_data="a:cancel"),
            ]
        ]
    )
