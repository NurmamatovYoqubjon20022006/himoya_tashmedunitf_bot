"""Admin panel handlerlari."""
from __future__ import annotations

import asyncio

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Faculty, IncidentType, Report, ReportStatus, UserType
from bot.database.queries import (
    append_admin_note,
    get_report_with_attachments,
    list_reports,
    list_user_ids,
    stats_summary,
    update_report_status,
)
from bot.filters.admin import IsAdmin
from bot.keyboards.admin import (
    admin_main_menu,
    confirm_broadcast,
    cancel_inline,
    report_actions,
    reports_pagination,
)
from bot.keyboards.main import main_menu
from bot.states.admin import AdminSG
from bot.utils.i18n import t

router = Router(name="admin")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


STATUS_LABELS: dict[ReportStatus, str] = {
    ReportStatus.NEW: "🆕 Yangi",
    ReportStatus.IN_REVIEW: "🔍 Ko'rib chiqilmoqda",
    ReportStatus.RESOLVED: "✅ Hal qilingan",
    ReportStatus.REJECTED: "❌ Rad etilgan",
}

INCIDENT_LABELS: dict[IncidentType, str] = {
    IncidentType.HARASSMENT: "Shilqimlik",
    IncidentType.PRESSURE: "Tazyiq",
    IncidentType.VIOLENCE: "Zo'ravonlik",
    IncidentType.DISCRIMINATION: "Kamsitish",
    IncidentType.OTHER: "Boshqa",
}

USER_TYPE_LABELS: dict[UserType, str] = {
    UserType.STUDENT: "Talaba",
    UserType.MASTER: "Magistrant",
    UserType.TEACHER: "O'qituvchi",
    UserType.STAFF: "Universitet xodimi",
    UserType.OTHER: "Boshqa",
}

FACULTY_LABELS_ADM: dict[Faculty, str] = {
    Faculty.DAVOLASH_1: "1-son Davolash",
    Faculty.DAVOLASH_2: "2-son Davolash",
    Faculty.PEDIATRIYA: "Pediatriya",
    Faculty.XALQARO: "Xalqaro ta'lim",
}


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "👮 <b>Admin panel</b>\n\nSiz administrativ ko'rinishdasiz. "
        "Quyidagi bo'limlardan birini tanlang:",
        reply_markup=admin_main_menu(),
    )


@router.message(F.text == "🚪 Admin paneldan chiqish")
async def admin_exit(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    from bot.database.queries import get_or_create_user

    user = await get_or_create_user(session, message.from_user.id)
    await state.clear()
    await message.answer(
        "Admin paneldan chiqdingiz.",
        reply_markup=main_menu(user.language),
    )


# ===================== RO'YXAT =====================

STATUS_BTN_MAP: dict[str, ReportStatus | None] = {
    "🆕 Yangi murojaatlar": ReportStatus.NEW,
    "🔍 Ko'rib chiqilmoqda": ReportStatus.IN_REVIEW,
    "✅ Hal qilingan": ReportStatus.RESOLVED,
    "❌ Rad etilgan": ReportStatus.REJECTED,
}


@router.message(F.text.in_(set(STATUS_BTN_MAP.keys())))
async def list_by_status(message: Message, session: AsyncSession) -> None:
    status = STATUS_BTN_MAP[message.text]
    await _render_list(message, session, status, page=1)


@router.callback_query(F.data.startswith("a:list:"))
async def cb_list(call: CallbackQuery, session: AsyncSession) -> None:
    _, _, key, page_s = call.data.split(":", 3)
    page = int(page_s)
    status: ReportStatus | None = None
    if key != "all":
        try:
            status = ReportStatus(key)
        except ValueError:
            status = None
    await _render_list(call.message, session, status, page=page, edit=True)
    await call.answer()


async def _render_list(
    message: Message,
    session: AsyncSession,
    status: ReportStatus | None,
    page: int,
    edit: bool = False,
) -> None:
    reports, total_pages = await list_reports(session, status=status, page=page)
    title_status = STATUS_LABELS[status] if status else "📋 Barcha murojaatlar"

    if not reports:
        text = f"{title_status}\n\nHozircha hech narsa yo'q."
        if edit:
            await message.edit_text(text)
        else:
            await message.answer(text)
        return

    lines = [f"<b>{title_status}</b>", ""]
    for r in reports:
        lines.append(
            f"🆔 <code>{r.tracking_id}</code> | "
            f"{INCIDENT_LABELS.get(r.incident_type, r.incident_type.value)} | "
            f"{STATUS_LABELS.get(r.status, r.status.value)}\n"
            f"   📅 {r.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"   /r_{r.id}"
        )
        lines.append("")

    text = "\n".join(lines)
    key = status.value if status else "all"
    kb = reports_pagination(page, total_pages, status_filter=key)

    if edit:
        await message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=kb, parse_mode="HTML")


# ===================== BITTA MUROJAAT =====================


@router.message(F.text.regexp(r"^/r_(\d+)$").as_("m"))
async def show_report(message: Message, m, session: AsyncSession) -> None:
    rid = int(m.group(1))
    await _render_report(message, session, rid)


async def _render_report(
    message: Message, session: AsyncSession, rid: int, edit: bool = False
) -> None:
    r = await get_report_with_attachments(session, rid)
    if r is None:
        text = "❌ Murojaat topilmadi."
        if edit:
            await message.edit_text(text)
        else:
            await message.answer(text)
        return

    # Murojaatchi ma'lumotlari
    user_block = ""
    if r.user_id is not None:
        from bot.database.models import User
        user = await session.get(User, r.user_id)
        if user:
            lines = ["\n👤 <b>Murojaatchi:</b>"]
            lines.append(f"  • F.I.O: {user.full_name or '—'}")
            lines.append(f"  • Telefon: <code>{user.phone or '—'}</code>")
            if user.user_type:
                lines.append(f"  • Maqom: {USER_TYPE_LABELS.get(user.user_type, '—')}")
            if user.faculty:
                lines.append(f"  • Fakultet: {FACULTY_LABELS_ADM.get(user.faculty, '—')}")
            if user.course:
                lines.append(f"  • Kurs: {user.course}")
            if user.direction:
                lines.append(f"  • Yo'nalish: {user.direction}")
            if user.group_name:
                lines.append(f"  • Guruh: {user.group_name}")
            if user.position:
                lines.append(f"  • Lavozim: {user.position}")
            if user.username:
                lines.append(f"  • Telegram: @{user.username}")
            user_block = "\n".join(lines) + "\n"

    text = (
        f"📋 <b>Murojaat #{r.tracking_id}</b>\n\n"
        f"<b>Holati:</b> {STATUS_LABELS.get(r.status, r.status.value)}\n"
        f"<b>Turi:</b> {INCIDENT_LABELS.get(r.incident_type, r.incident_type.value)}\n"
        f"<b>Joy:</b> {r.location or '—'}\n"
        f"<b>Vaqt (voqea):</b> {r.incident_date or '—'}\n"
        f"<b>Yaratilgan:</b> {r.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        f"<b>Yangilangan:</b> {r.updated_at.strftime('%Y-%m-%d %H:%M')}\n"
        f"<b>Fayllar:</b> {len(r.attachments)} ta\n"
        f"{user_block}"
        f"\n<b>Tafsilot:</b>\n{r.description}"
    )
    if r.admin_note:
        text += f"\n\n<b>Komissiya izohlari:</b>{r.admin_note}"

    kb = report_actions(r.id, r.status)
    if edit:
        await message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("a:status:"))
async def cb_change_status(
    call: CallbackQuery, session: AsyncSession, bot: Bot
) -> None:
    _, _, rid_s, new_status = call.data.split(":", 3)
    rid = int(rid_s)
    try:
        status = ReportStatus(new_status)
    except ValueError:
        await call.answer("Noto'g'ri status")
        return
    await update_report_status(session, rid, status)
    await call.answer(f"Holat yangilandi: {STATUS_LABELS[status]}", show_alert=False)
    await _render_report(call.message, session, rid, edit=True)
    await _notify_user_status(bot, session, rid, status)


async def _notify_user_status(
    bot: Bot, session: AsyncSession, rid: int, status: ReportStatus
) -> None:
    """Murojaat egasiga holat o'zgargani haqida xabar yuborish."""
    r = await get_report_with_attachments(session, rid)
    if r is None or r.user_id is None:
        return
    from bot.database.models import User

    user = await session.get(User, r.user_id)
    if user is None:
        return
    try:
        await bot.send_message(
            user.telegram_id,
            f"📋 Murojaatingiz <code>{r.tracking_id}</code> holati yangilandi:\n\n"
            f"<b>{STATUS_LABELS.get(status, status.value)}</b>"
            + (f"\n\n<b>Izoh:</b>{r.admin_note}" if r.admin_note else ""),
            parse_mode="HTML",
        )
    except Exception:
        logger.exception(f"Foydalanuvchiga xabar yuborib bo'lmadi: {user.telegram_id}")


@router.callback_query(F.data.startswith("a:files:"))
async def cb_show_files(
    call: CallbackQuery, session: AsyncSession, bot: Bot
) -> None:
    rid = int(call.data.split(":")[2])
    r = await get_report_with_attachments(session, rid)
    if r is None or not r.attachments:
        await call.answer("Fayllar yo'q", show_alert=True)
        return
    await call.answer(f"{len(r.attachments)} ta fayl yuborilmoqda...")
    for att in r.attachments:
        try:
            if att.file_type == "photo":
                await bot.send_photo(call.from_user.id, att.file_id)
            elif att.file_type == "video":
                await bot.send_video(call.from_user.id, att.file_id)
            elif att.file_type == "audio":
                await bot.send_voice(call.from_user.id, att.file_id)
            elif att.file_type == "document":
                await bot.send_document(call.from_user.id, att.file_id)
        except Exception:
            logger.exception(f"File yuborilmadi: {att.file_id}")


# ===================== IZOH QO'SHISH =====================


@router.callback_query(F.data.startswith("a:note:"))
async def cb_add_note_start(
    call: CallbackQuery, state: FSMContext
) -> None:
    rid = int(call.data.split(":")[2])
    await state.set_state(AdminSG.waiting_note)
    await state.update_data(report_id=rid)
    await call.message.answer(
        "📝 Izoh matnini yozing (komissiya izohi sifatida saqlanadi va "
        "murojaat egasiga ko'rinadi):",
        reply_markup=cancel_inline(),
    )
    await call.answer()


@router.message(AdminSG.waiting_note, F.text)
async def admin_save_note(
    message: Message, state: FSMContext, session: AsyncSession, bot: Bot
) -> None:
    data = await state.get_data()
    rid = data.get("report_id")
    if not rid:
        await state.clear()
        return
    author = message.from_user.full_name or "admin"
    report = await append_admin_note(session, rid, message.text, author=author)
    await state.clear()
    if report:
        await message.answer("✅ Izoh saqlandi.", reply_markup=admin_main_menu())
        await _render_report(message, session, rid)
        await _notify_user_status(bot, session, rid, report.status)
    else:
        await message.answer("❌ Murojaat topilmadi.")


@router.callback_query(F.data == "a:cancel")
async def cb_cancel(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Bekor qilindi.", reply_markup=admin_main_menu())
    await call.answer()


@router.callback_query(F.data == "a:noop")
async def cb_noop(call: CallbackQuery) -> None:
    await call.answer()


# ===================== STATISTIKA =====================


@router.message(F.text == "📊 Statistika")
async def show_stats(message: Message, session: AsyncSession) -> None:
    s = await stats_summary(session)
    text = (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{s['users']}</b>\n"
        f"📋 Jami murojaatlar: <b>{s['total']}</b>\n\n"
        "<b>Holat bo'yicha:</b>\n"
        f"  🆕 Yangi: {s['st_new']}\n"
        f"  🔍 Ko'rib chiqilmoqda: {s['st_in_review']}\n"
        f"  ✅ Hal qilingan: {s['st_resolved']}\n"
        f"  ❌ Rad etilgan: {s['st_rejected']}\n\n"
        "<b>Hodisa turi bo'yicha:</b>\n"
        f"  Shilqimlik: {s['tp_harassment']}\n"
        f"  Tazyiq: {s['tp_pressure']}\n"
        f"  Zo'ravonlik: {s['tp_violence']}\n"
        f"  Kamsitish: {s['tp_discrimination']}\n"
        f"  Boshqa: {s['tp_other']}"
    )
    await message.answer(text, parse_mode="HTML")


# ===================== ID BO'YICHA QIDIRISH =====================


@router.message(F.text == "🔎 ID bo'yicha qidirish")
async def search_start(message: Message, state: FSMContext) -> None:
    await state.set_state(AdminSG.waiting_search)
    await message.answer(
        "🆔 Murojaat tracking ID'sini kiriting (masalan: H-AB12CD34):",
        reply_markup=cancel_inline(),
    )


@router.message(AdminSG.waiting_search, F.text)
async def search_lookup(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    from bot.database.queries import get_report_by_tracking_id

    tid = message.text.strip().upper()
    await state.clear()
    r = await get_report_by_tracking_id(session, tid)
    if r is None:
        await message.answer("❌ Topilmadi.", reply_markup=admin_main_menu())
        return
    await _render_report(message, session, r.id)


# ===================== BROADCAST =====================


@router.message(F.text == "📢 Broadcast")
async def broadcast_start(message: Message, state: FSMContext) -> None:
    await state.set_state(AdminSG.waiting_broadcast)
    await message.answer(
        "📢 Barcha foydalanuvchilarga yuboriladigan xabar matnini yozing:",
        reply_markup=cancel_inline(),
    )


@router.message(AdminSG.waiting_broadcast, F.text)
async def broadcast_preview(message: Message, state: FSMContext) -> None:
    await state.update_data(text=message.text)
    await message.answer(
        f"<b>Quyidagi xabar yuboriladi:</b>\n\n{message.text}",
        reply_markup=confirm_broadcast(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "a:broadcast:send")
async def broadcast_send(
    call: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot
) -> None:
    data = await state.get_data()
    text = data.get("text")
    await state.clear()
    if not text:
        await call.answer("Matn yo'q", show_alert=True)
        return

    user_ids = await list_user_ids(session)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(f"📨 Yuborilmoqda... ({len(user_ids)} ta foydalanuvchi)")

    sent = 0
    failed = 0
    for tid in user_ids:
        try:
            await bot.send_message(tid, text)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)  # ~20 req/sec

    await call.message.answer(
        f"✅ Yakunlandi.\nYuborildi: <b>{sent}</b>\nXatolik: <b>{failed}</b>",
        reply_markup=admin_main_menu(),
        parse_mode="HTML",
    )
    await call.answer()
