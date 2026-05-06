"""DB CRUD operatsiyalari."""
from __future__ import annotations

import secrets
import string
from datetime import datetime, timezone

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.database.models import (
    Attachment,
    Faculty,
    IncidentType,
    Report,
    ReportStatus,
    User,
    UserType,
)


def _invalidate_cache(telegram_id: int) -> None:
    """Cache yo'q — bu funksiya backward compat uchun bo'sh qoldirildi."""
    pass


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None = None,
) -> User:
    """Har safar DB'dan o'qiymiz — User obyekti session'ga bog'liq.

    Cache yo'q (cross-session bug bor edi); PostgreSQL PK lookup ~1ms.
    """
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        user = User(telegram_id=telegram_id, username=username)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    elif username and user.username != username:
        user.username = username
        await session.commit()
    return user


async def set_user_language(
    session: AsyncSession, telegram_id: int, language: str
) -> None:
    user = await get_or_create_user(session, telegram_id)
    user.language = language
    await session.commit()


async def is_phone_taken(
    session: AsyncSession, phone: str, exclude_telegram_id: int | None = None
) -> bool:
    """Telefon raqami allaqachon ro'yxatdan o'tganmi?"""
    stmt = select(User).where(User.phone == phone)
    if exclude_telegram_id is not None:
        stmt = stmt.where(User.telegram_id != exclude_telegram_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None


async def register_user(
    session: AsyncSession,
    telegram_id: int,
    *,
    phone: str,
    full_name: str,
    user_type: UserType,
    faculty: Faculty | None = None,
    course: int | None = None,
    direction: str | None = None,
    group_name: str | None = None,
    position: str | None = None,
) -> User:
    """Foydalanuvchini ro'yxatdan o'tkazish (yoki profilini yangilash).

    Cache'ni chetlab o'tib to'g'ridan-to'g'ri DB'dan o'qiymiz —
    ob'ekt joriy session'ga bog'langan bo'lishi shart.
    """
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        user = User(telegram_id=telegram_id)
        session.add(user)
        await session.flush()

    user.phone = phone
    user.full_name = full_name
    user.user_type = user_type
    user.faculty = faculty
    user.course = course
    user.direction = direction
    user.group_name = group_name
    user.position = position
    user.is_registered = True
    user.registered_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(user)
    _invalidate_cache(telegram_id)
    return user


async def get_user_by_phone(
    session: AsyncSession, phone: str
) -> User | None:
    result = await session.execute(select(User).where(User.phone == phone))
    return result.scalar_one_or_none()


async def list_user_reports(
    session: AsyncSession, user_id: int, limit: int = 20
) -> list[Report]:
    """Foydalanuvchining murojaatlari (eng yangidan)."""
    stmt = (
        select(Report)
        .where(Report.user_id == user_id)
        .order_by(desc(Report.created_at))
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


def _generate_tracking_id() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "H-" + "".join(secrets.choice(alphabet) for _ in range(8))


async def create_report(
    session: AsyncSession,
    *,
    user_id: int | None,
    incident_type: IncidentType,
    description: str,
    location: str | None = None,
    incident_date: str | None = None,
    is_anonymous: bool = True,
    attachments: list[tuple[str, str]] | None = None,
) -> Report:
    """Yangi murojaat yaratish.

    attachments: [(file_id, file_type), ...]
    """
    tracking_id = _generate_tracking_id()
    while await session.scalar(
        select(Report).where(Report.tracking_id == tracking_id)
    ):
        tracking_id = _generate_tracking_id()

    report = Report(
        tracking_id=tracking_id,
        user_id=user_id,
        incident_type=incident_type,
        description=description,
        location=location,
        incident_date=incident_date,
        is_anonymous=is_anonymous,
    )
    session.add(report)
    await session.flush()

    if attachments:
        for file_id, file_type in attachments:
            session.add(
                Attachment(
                    report_id=report.id,
                    file_id=file_id,
                    file_type=file_type,
                )
            )

    await session.commit()
    await session.refresh(report)
    return report


async def get_report_by_tracking_id(
    session: AsyncSession, tracking_id: str
) -> Report | None:
    result = await session.execute(
        select(Report).where(Report.tracking_id == tracking_id.upper())
    )
    return result.scalar_one_or_none()


async def update_report_status(
    session: AsyncSession,
    report_id: int,
    status: ReportStatus,
    admin_note: str | None = None,
) -> None:
    report = await session.get(Report, report_id)
    if report:
        report.status = status
        if admin_note is not None:
            report.admin_note = admin_note
        await session.commit()


async def list_reports(
    session: AsyncSession,
    status: ReportStatus | None = None,
    page: int = 1,
    per_page: int = 5,
) -> tuple[list[Report], int]:
    """Murojaatlarni sahifalab olish (status bo'yicha filter)."""
    base = select(Report)
    if status:
        base = base.where(Report.status == status)

    total = await session.scalar(
        select(func.count()).select_from(base.subquery())
    ) or 0
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    stmt = (
        base.order_by(desc(Report.created_at))
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all()), total_pages


async def get_report_with_attachments(
    session: AsyncSession, report_id: int
) -> Report | None:
    stmt = (
        select(Report)
        .options(selectinload(Report.attachments))
        .where(Report.id == report_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def append_admin_note(
    session: AsyncSession, report_id: int, note: str, author: str = ""
) -> Report | None:
    report = await session.get(Report, report_id)
    if report is None:
        return None
    prefix = f"\n— {author}: " if author else "\n— "
    report.admin_note = (report.admin_note or "") + prefix + note.strip()
    await session.commit()
    await session.refresh(report)
    return report


async def stats_summary(session: AsyncSession) -> dict[str, int]:
    """Statistika: jami, holatlar bo'yicha, turlar bo'yicha."""
    total = await session.scalar(select(func.count()).select_from(Report)) or 0

    by_status: dict[str, int] = {}
    for s in ReportStatus:
        c = await session.scalar(
            select(func.count()).where(Report.status == s)
        ) or 0
        by_status[s.value] = c

    by_type: dict[str, int] = {}
    for t in IncidentType:
        c = await session.scalar(
            select(func.count()).where(Report.incident_type == t)
        ) or 0
        by_type[t.value] = c

    users_total = await session.scalar(
        select(func.count()).select_from(User)
    ) or 0

    return {
        "total": total,
        "users": users_total,
        **{f"st_{k}": v for k, v in by_status.items()},
        **{f"tp_{k}": v for k, v in by_type.items()},
    }


async def list_user_ids(session: AsyncSession) -> list[int]:
    """Broadcast uchun barcha foydalanuvchi telegram_id'lari."""
    result = await session.execute(
        select(User.telegram_id).where(User.is_blocked == False)  # noqa: E712
    )
    return [row[0] for row in result.all()]
