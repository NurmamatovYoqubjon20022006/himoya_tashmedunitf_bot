"""To'liq bot E2E testi.

Tekshiradi:
1. Modullar import
2. Routerlar
3. i18n kalitlari (uz/ru/en)
4. DB schema
5. CRUD operatsiyalar (User registratsiyasi + Report)
6. FSM states
7. Keyboards
8. Filters va Middlewares
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


results: list[tuple[str, bool, str]] = []


def ok(name: str, cond: bool, detail: str = "") -> None:
    results.append((name, cond, detail))
    mark = "[PASS]" if cond else "[FAIL]"
    print(f"  {mark} {name}" + (f" — {detail}" if detail else ""))


async def test_imports() -> None:
    print("\n[1] Modullarni import qilish")

    try:
        from config import settings  # noqa: F401
        ok("config.settings", True)
    except Exception as e:
        ok("config.settings", False, str(e))
        return

    try:
        from bot.database.models import (  # noqa: F401
            AdminUser, Attachment, Base, Faculty, IncidentType,
            Report, ReportStatus, User, UserRole, UserType,
        )
        ok("bot.database.models (yangi: UserType, Faculty)", True)
    except Exception as e:
        ok("bot.database.models", False, str(e))
        return

    try:
        from bot.database.queries import (  # noqa: F401
            append_admin_note, create_report, get_or_create_user,
            get_report_by_tracking_id, get_report_with_attachments,
            get_user_by_phone, is_phone_taken, list_reports,
            list_user_ids, list_user_reports, register_user,
            set_user_language, stats_summary, update_report_status,
        )
        ok("bot.database.queries (14 ta funksiya)", True)
    except Exception as e:
        ok("bot.database.queries", False, str(e))

    try:
        from bot.handlers import router as root_router
        ok("bot.handlers.router", True, f"{len(root_router.sub_routers)} sub-router")
    except Exception as e:
        ok("bot.handlers.router", False, str(e))

    try:
        from bot.handlers import admin, faq, registration, report, start, status  # noqa
        ok("Hamma handler modullari", True)
    except Exception as e:
        ok("Handlerlar", False, str(e))

    try:
        from bot.keyboards.main import (  # noqa
            cancel_kb, confirm_kb, done_skip_cancel_kb, incident_type_kb,
            language_kb, main_menu, skip_cancel_kb,
        )
        from bot.keyboards.registration import (  # noqa
            FACULTY_LABELS, cancel_only_kb, confirm_registration_kb,
            contact_kb, course_kb, faculty_kb, skip_or_cancel_kb,
            user_type_kb,
        )
        from bot.keyboards.admin import (  # noqa
            admin_main_menu, cancel_inline, confirm_broadcast,
            report_actions, reports_pagination,
        )
        ok("Klaviaturalar (main, registration, admin)", True)
    except Exception as e:
        ok("Klaviaturalar", False, str(e))

    try:
        from bot.states.report import ReportSG, StatusSG  # noqa
        from bot.states.admin import AdminSG  # noqa
        from bot.states.registration import ProfileSG, RegistrationSG  # noqa
        ok("FSM states (4 ta StatesGroup)", True)
    except Exception as e:
        ok("FSM states", False, str(e))

    try:
        from bot.middlewares.db import DbSessionMiddleware  # noqa
        from bot.middlewares.throttling import ThrottlingMiddleware  # noqa
        from bot.filters.admin import IsAdmin  # noqa
        from bot.utils.i18n import t
        from bot.utils.logger import setup_logger  # noqa
        ok("Middlewares, filters, utils", True)
    except Exception as e:
        ok("Middleware/filter/utils", False, str(e))


async def test_i18n() -> None:
    print("\n[2] i18n kalitlari")
    from bot.utils.i18n import t, _load

    KEYS_REQUIRED = [
        "start.welcome", "start.need_register", "start.welcome_back",
        "menu.report", "menu.my_reports", "menu.profile", "menu.status",
        "menu.faq", "menu.contacts", "menu.language", "menu.cancel",
        "menu.skip", "menu.done", "menu.back",
        "lang.choose", "lang.set",

        "reg.start", "reg.share_contact", "reg.phone_invalid",
        "reg.phone_taken", "reg.ask_full_name", "reg.name_too_short",
        "reg.ask_user_type", "reg.type.student", "reg.type.master",
        "reg.type.teacher", "reg.type.staff", "reg.type.other",
        "reg.ask_faculty", "reg.ask_course", "reg.ask_direction",
        "reg.direction_too_short", "reg.ask_group", "reg.ask_position",
        "reg.confirm_title", "reg.confirm.send", "reg.confirm.restart",
        "reg.success", "reg.cancelled",

        "report.intro", "report.type.harassment", "report.type.pressure",
        "report.type.violence", "report.type.discrimination",
        "report.type.other", "report.ask_description", "report.too_short",
        "report.confirm", "report.confirm.send",
        "report.success", "report.cancelled",
        "report.feedback_type", "report.feedback_description", "report.back_done",

        "my_reports.title", "my_reports.empty", "my_reports.item",

        "profile.title", "profile.faculty", "profile.course",
        "profile.direction", "profile.group", "profile.position",

        "fac.davolash_1", "fac.davolash_2", "fac.pediatriya", "fac.xalqaro",
        "ut.student", "ut.master", "ut.teacher", "ut.staff", "ut.other",

        "status.ask_id", "status.not_found", "status.info", "status.note",
        "status.new", "status.in_review", "status.resolved", "status.rejected",

        "faq.title", "contacts.title",

        "common.error", "common.cancelled", "common.choose_option",
        "common.not_registered",
    ]

    uz = _load("uz")
    missing_uz = [k for k in KEYS_REQUIRED if k not in uz]
    ok(
        "uz.json hamma kalit bor",
        not missing_uz,
        f"yetishmayotgan: {missing_uz[:5]}" if missing_uz else f"{len(KEYS_REQUIRED)} kalit",
    )

    # ru/en uchun fallback uz'ga ishlashi kerak
    fallback = t("reg.start", "ru")
    ok(
        "ru/en fallback uz'ga ishlaydi",
        fallback != "reg.start" and len(fallback) > 10,
        f"len={len(fallback)}",
    )

    # placeholderni format qiladi
    formatted = t("reg.confirm_title", "uz", full_name="X", phone="+1", user_type="A", extra="")
    ok(
        "i18n placeholder formati ishlaydi",
        "X" in formatted and "+1" in formatted,
        "format() ishladi",
    )


async def test_db_schema() -> None:
    print("\n[3] DB schema")
    from sqlalchemy import inspect, text
    from bot.database.db import async_session, engine

    async with engine.begin() as conn:
        def check(sync_conn):
            insp = inspect(sync_conn)
            cols = {c["name"] for c in insp.get_columns("users")}
            return cols

        cols = await conn.run_sync(check)

        REQUIRED = {
            "id", "telegram_id", "username", "language", "role",
            "phone", "full_name", "user_type", "faculty", "course",
            "direction", "group_name", "position", "is_registered",
            "registered_at", "is_blocked", "created_at",
        }
        missing = REQUIRED - cols
        ok(
            "users jadvalida hamma maydon bor",
            not missing,
            f"yetishmayotgan: {missing}" if missing else f"{len(cols)} ta column",
        )

    async with async_session() as s:
        # Phone unique index
        idx = await s.execute(text(
            "SELECT indexname FROM pg_indexes WHERE tablename='users' AND indexname='ix_users_phone'"
        ))
        ok("ix_users_phone unique index", idx.scalar() is not None)

        # ENUM tiplari mavjud
        types = await s.execute(text(
            "SELECT typname FROM pg_type WHERE typname IN ('UserType', 'Faculty')"
        ))
        type_names = {row[0] for row in types}
        ok(
            "ENUM tiplari yaratilgan",
            type_names == {"UserType", "Faculty"},
            f"topildi: {type_names}",
        )


async def test_crud() -> None:
    print("\n[4] CRUD operatsiyalar (E2E)")
    import secrets
    from sqlalchemy import delete, text

    from bot.database.db import async_session
    from bot.database.models import (
        Faculty, IncidentType, Report, ReportStatus, User, UserType,
    )
    from bot.database.queries import (
        append_admin_note, create_report, get_or_create_user,
        get_report_by_tracking_id, get_report_with_attachments,
        get_user_by_phone, is_phone_taken, list_reports,
        list_user_ids, list_user_reports, register_user,
        set_user_language, stats_summary, update_report_status,
    )

    test_tg_id = 999_000_000 + secrets.randbelow(10_000)
    test_phone = "+99890" + str(secrets.randbelow(10_000_000)).zfill(7)

    async with async_session() as s:
        # 1. get_or_create_user
        user = await get_or_create_user(s, telegram_id=test_tg_id, username="test_e2e")
        ok("get_or_create_user (yangi)", user.id is not None and not user.is_registered)

        # 2. is_phone_taken — bo'sh phone
        taken = await is_phone_taken(s, test_phone)
        ok("is_phone_taken (bo'sh)", taken is False)

        # 3. set_user_language
        await set_user_language(s, test_tg_id, "ru")
        u2 = await get_or_create_user(s, telegram_id=test_tg_id)
        ok("set_user_language", u2.language == "ru")

        # 4. register_user
        registered = await register_user(
            s,
            telegram_id=test_tg_id,
            phone=test_phone,
            full_name="E2E Test User",
            user_type=UserType.STUDENT,
            faculty=Faculty.PEDIATRIYA,
            course=3,
            direction="Pediatriya yo'nalishi",
            group_name="301-A",
        )
        ok(
            "register_user",
            registered.is_registered
            and registered.phone == test_phone
            and registered.user_type == UserType.STUDENT
            and registered.faculty == Faculty.PEDIATRIYA
            and registered.course == 3
            and registered.direction == "Pediatriya yo'nalishi",
        )

        # 5. is_phone_taken — endi taken
        taken = await is_phone_taken(s, test_phone)
        ok("is_phone_taken (registered)", taken is True)

        # 6. exclude_telegram_id
        not_taken = await is_phone_taken(s, test_phone, exclude_telegram_id=test_tg_id)
        ok("is_phone_taken exclude self", not_taken is False)

        # 7. get_user_by_phone
        by_phone = await get_user_by_phone(s, test_phone)
        ok("get_user_by_phone", by_phone is not None and by_phone.id == registered.id)

        # 8. create_report
        report = await create_report(
            s,
            user_id=registered.id,
            incident_type=IncidentType.HARASSMENT,
            description="E2E test description with at least 20 characters",
            location="Test joy",
            incident_date="2026-05-06",
            is_anonymous=False,
            attachments=[("test_file_id_123", "photo")],
        )
        ok(
            "create_report (attachment bilan)",
            report.tracking_id.startswith("H-") and len(report.tracking_id) == 10,
        )

        # 9. get_report_by_tracking_id
        found = await get_report_by_tracking_id(s, report.tracking_id)
        ok("get_report_by_tracking_id", found is not None and found.id == report.id)

        # 10. lowercase tracking_id ham ishlaydi
        found_lower = await get_report_by_tracking_id(s, report.tracking_id.lower())
        ok("get_report_by_tracking_id (lowercase)", found_lower is not None)

        # 11. get_report_with_attachments
        with_att = await get_report_with_attachments(s, report.id)
        ok(
            "get_report_with_attachments",
            with_att is not None and len(with_att.attachments) == 1,
        )

        # 12. update_report_status
        await update_report_status(s, report.id, ReportStatus.IN_REVIEW)
        updated = await get_report_by_tracking_id(s, report.tracking_id)
        ok("update_report_status", updated.status == ReportStatus.IN_REVIEW)

        # 13. append_admin_note
        with_note = await append_admin_note(s, report.id, "E2E izoh", "tester")
        ok(
            "append_admin_note",
            with_note is not None
            and "E2E izoh" in (with_note.admin_note or ""),
        )

        # 14. list_reports (pagination)
        page1, total_pages = await list_reports(s, page=1, per_page=5)
        ok("list_reports pagination", isinstance(page1, list) and total_pages >= 1)

        # 15. list_reports filtered
        in_review, _ = await list_reports(s, status=ReportStatus.IN_REVIEW)
        ok(
            "list_reports filtered",
            all(r.status == ReportStatus.IN_REVIEW for r in in_review),
        )

        # 16. list_user_reports
        my_reports = await list_user_reports(s, registered.id)
        ok(
            "list_user_reports",
            len(my_reports) >= 1 and my_reports[0].id == report.id,
        )

        # 17. list_user_ids
        all_ids = await list_user_ids(s)
        ok(
            "list_user_ids",
            test_tg_id in all_ids and len(all_ids) >= 1,
        )

        # 18. stats_summary
        stats = await stats_summary(s)
        ok(
            "stats_summary",
            stats["total"] >= 1 and "users" in stats and "st_in_review" in stats,
            f"total={stats['total']}, users={stats['users']}",
        )

    # report_id va user_id'ni alohida saqlaymiz
    report_id = report.id
    user_pk = registered.id

    # 19. duplicate phone — alohida sessiyada (rollback effektidan qochish uchun)
    another_tg = test_tg_id + 1
    async with async_session() as s2:
        await get_or_create_user(s2, telegram_id=another_tg, username="dup")
        try:
            await register_user(
                s2,
                telegram_id=another_tg,
                phone=test_phone,  # SHU TELEFON RAQAMI BAND!
                full_name="Duplicate",
                user_type=UserType.STUDENT,
            )
            ok("duplicate phone IntegrityError", False, "exception bo'lishi kerak edi")
        except Exception as e:
            ok(
                "duplicate phone IntegrityError",
                "unique" in str(e).lower() or "duplicate" in str(e).lower(),
            )

    # CLEANUP — alohida sessiyada (Attachment'lar CASCADE bilan o'chadi)
    from bot.database.models import Attachment
    async with async_session() as s_cleanup:
        await s_cleanup.execute(delete(Attachment).where(Attachment.report_id == report_id))
        await s_cleanup.execute(delete(Report).where(Report.id == report_id))
        await s_cleanup.execute(
            delete(User).where(User.telegram_id.in_([test_tg_id, another_tg]))
        )
        await s_cleanup.commit()
    ok("CLEANUP — test ma'lumotlarini o'chirish", True)


async def test_handler_routing() -> None:
    print("\n[5] Handler routing")
    from aiogram import Dispatcher
    from aiogram.fsm.storage.memory import MemoryStorage
    from bot.handlers import router as root_router
    from bot.middlewares.db import DbSessionMiddleware
    from bot.middlewares.throttling import ThrottlingMiddleware

    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(DbSessionMiddleware())
    dp.message.middleware(ThrottlingMiddleware(rate=0.1))
    dp.include_router(root_router)
    ok("Dispatcher router include", True, "exception bermadi")

    # Sub-router nomlari
    names = [r.name for r in root_router.sub_routers]
    expected = {"admin", "registration", "start", "report", "status", "faq"}
    ok(
        "Hamma sub-router ulangan",
        expected.issubset(set(names)),
        f"topildi: {names}",
    )


async def test_keyboards() -> None:
    print("\n[6] Keyboards (callback_data va format)")
    from bot.database.models import Faculty
    from bot.keyboards.registration import (
        confirm_registration_kb, contact_kb, course_kb,
        faculty_kb, user_type_kb,
    )
    from bot.keyboards.main import incident_type_kb, main_menu

    kb = main_menu("uz")
    ok(
        "main_menu (4 qator)",
        len(kb.keyboard) == 4,
        f"qatorlar: {len(kb.keyboard)}",
    )

    contact = contact_kb("uz")
    ok(
        "contact_kb (request_contact=True)",
        contact.keyboard[0][0].request_contact is True,
    )

    types = user_type_kb("uz")
    callback_datas = [b.callback_data for row in types.inline_keyboard for b in row]
    ok(
        "user_type_kb 5 ta callback",
        len(callback_datas) == 5
        and all(cd.startswith("reg_type:") for cd in callback_datas),
    )

    fac = faculty_kb()
    fac_data = [b.callback_data for row in fac.inline_keyboard for b in row]
    ok(
        "faculty_kb 4 ta fakultet",
        len(fac_data) == 4
        and {f"reg_fac:{f.value}" for f in Faculty} == set(fac_data),
    )

    courses = course_kb()
    course_data = [b.callback_data for row in courses.inline_keyboard for b in row]
    ok(
        "course_kb (1-7)",
        len(course_data) == 7
        and all(cd.startswith("reg_course:") for cd in course_data),
    )

    incident = incident_type_kb("uz")
    inc_data = [b.callback_data for row in incident.inline_keyboard for b in row]
    ok(
        "incident_type_kb 5 ta tur",
        len(inc_data) == 5,
    )


async def test_phone_validation() -> None:
    print("\n[7] Phone validation")
    from bot.handlers.registration import _normalize_phone

    ok("+998901234567", _normalize_phone("+998901234567") == "+998901234567")
    ok("998901234567 (no +)", _normalize_phone("998901234567") == "+998901234567")
    ok("with spaces", _normalize_phone("+998 90 123 45 67") == "+998901234567")
    ok("with dashes", _normalize_phone("+998-90-123-45-67") == "+998901234567")
    ok("invalid (too short)", _normalize_phone("+1") is None)
    ok("invalid (letters)", _normalize_phone("abc") is None)
    ok("empty", _normalize_phone("") is None)


async def main() -> None:
    print("=" * 64)
    print("  HIMOYA BOT — E2E TEST")
    print("=" * 64)

    await test_imports()
    await test_i18n()
    await test_db_schema()
    await test_crud()
    await test_handler_routing()
    await test_keyboards()
    await test_phone_validation()

    total = len(results)
    passed = sum(1 for _, c, _ in results if c)
    failed = total - passed

    print("\n" + "=" * 64)
    print(f"  NATIJA: {passed}/{total} PASS  |  {failed} FAIL")
    print("=" * 64)

    if failed:
        print("\n  Muvaffaqiyatsiz testlar:")
        for name, cond, detail in results:
            if not cond:
                print(f"    - {name}: {detail}")
        sys.exit(1)
    else:
        print("\n  Hammasi muvaffaqiyatli!")


if __name__ == "__main__":
    asyncio.run(main())
