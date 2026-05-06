"""3-bosqichli murojaat oqimi: FSM state transitions, handler routing, DB write."""
from __future__ import annotations

import asyncio
import secrets
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


results: list[tuple[str, bool, str]] = []


def ok(name: str, cond: bool, detail: str = "") -> None:
    results.append((name, cond, detail))
    mark = "[PASS]" if cond else "[FAIL]"
    print(f"  {mark} {name}" + (f" — {detail}" if detail else ""))


async def main() -> None:
    print("=" * 64)
    print("  3-BOSQICHLI MUROJAAT OQIMI — FSM + HANDLER TEST")
    print("=" * 64)

    # 1. ReportSG endi 3 ta state
    print("\n[1] ReportSG soddalashtirilgani")
    from bot.states.report import ReportSG, StatusSG  # noqa
    states = [s.state for s in [ReportSG.incident_type, ReportSG.description, ReportSG.confirm]]
    ok("Faqat 3 ta state", len(states) == 3, str(states))

    # Olib tashlangan state'lar yo'qligini tekshir
    has_attachments = hasattr(ReportSG, "attachments")
    has_location = hasattr(ReportSG, "location")
    has_incident_date = hasattr(ReportSG, "incident_date")
    ok("attachments olib tashlangan", not has_attachments)
    ok("location olib tashlangan", not has_location)
    ok("incident_date olib tashlangan", not has_incident_date)

    # 2. Handler functions mavjud
    print("\n[2] Handler functions")
    from bot.handlers.report import (
        _show_step_1, _show_step_2, _show_step_3,
        on_incident_type, on_description,
        on_confirm_send, on_confirm_back, on_confirm_cancel,
        report_start, REPORT_TRIGGERS, BACK_TEXTS,
    )
    ok("_show_step_1, _show_step_2, _show_step_3 mavjud", True)
    ok("on_incident_type, on_description mavjud", True)
    ok("on_confirm_send, on_confirm_back, on_confirm_cancel mavjud", True)

    # 3. Triggerlar
    print("\n[3] Triggers")
    ok(
        "📝 Murojaat yuborish trigger'da",
        "📝 Murojaat yuborish" in REPORT_TRIGGERS,
    )
    ok(
        "Eski 🆘 Anonim ham trigger'da (back-compat)",
        "🆘 Anonim murojaat yuborish" in REPORT_TRIGGERS,
    )
    ok(
        "BACK_TEXTS to'g'ri",
        "⬅️ Orqaga" in BACK_TEXTS,
    )

    # 4. Keyboards
    print("\n[4] Keyboards (orqaga tugmasi)")
    from bot.keyboards.main import back_cancel_kb, confirm_kb, incident_type_kb

    bk = back_cancel_kb("uz")
    bk_texts = [b.text for row in bk.keyboard for b in row]
    ok("back_cancel_kb [⬅️ Orqaga + ❌ Bekor]",
       any("Orqaga" in t for t in bk_texts) and any("Bekor" in t for t in bk_texts))

    cf = confirm_kb("uz")
    cf_data = [b.callback_data for row in cf.inline_keyboard for b in row]
    ok("confirm_kb has back",
       "confirm:back" in cf_data and "confirm:send" in cf_data and "confirm:cancel" in cf_data,
       f"data: {cf_data}")

    inc = incident_type_kb("uz")
    inc_count = sum(len(row) for row in inc.inline_keyboard)
    ok("incident_type_kb 5 ta tur", inc_count == 5)

    # 5. DB CRUD oqimi (E2E murojaat yaratish)
    print("\n[5] DB E2E (registratsiya + 3-bosqich + report yaratish)")
    from bot.database.db import async_session
    from bot.database.models import (
        Faculty, IncidentType, Report, User, UserType, Attachment,
    )
    from bot.database.queries import (
        create_report, get_or_create_user, get_report_by_tracking_id,
        list_user_reports, register_user,
    )
    from sqlalchemy import delete

    test_tg = 999_888_000 + secrets.randbelow(99_999)
    test_phone = "+99890" + str(secrets.randbelow(10_000_000)).zfill(7)

    async with async_session() as s:
        await get_or_create_user(s, telegram_id=test_tg, username="flow_test")

    # Registratsiya
    async with async_session() as s:
        registered = await register_user(
            s,
            telegram_id=test_tg,
            phone=test_phone,
            full_name="Flow Test User",
            user_type=UserType.STUDENT,
            faculty=Faculty.DAVOLASH_1,
            course=2,
            direction="Davolash ishi",
            group_name="201-B",
        )
        user_pk = registered.id
        ok("register_user", registered.is_registered)

    # Murojaat — 3-bosqich (location, incident_date NULL)
    async with async_session() as s:
        report = await create_report(
            s,
            user_id=user_pk,
            incident_type=IncidentType.HARASSMENT,
            description="3-bosqichli oqim test description with at least 20 chars and detailed info",
            location=None,        # ENDI BO'SH
            incident_date=None,   # ENDI BO'SH
            is_anonymous=False,
        )
        report_id = report.id
        tid = report.tracking_id
        ok(
            "create_report (location=None, date=None)",
            report.tracking_id.startswith("H-")
            and report.location is None
            and report.incident_date is None
            and report.is_anonymous is False,
        )

    # Tracking ID orqali topish
    async with async_session() as s:
        found = await get_report_by_tracking_id(s, tid)
        ok("Tracking ID orqali topish", found is not None and found.id == report_id)
        ok("user_id to'g'ri ulangan", found.user_id == user_pk)

    # Foydalanuvchining murojaatlari
    async with async_session() as s:
        my = await list_user_reports(s, user_pk)
        ok("list_user_reports", len(my) == 1 and my[0].tracking_id == tid)

    # Phone unique constraint
    async with async_session() as s:
        from bot.database.queries import is_phone_taken
        taken = await is_phone_taken(s, test_phone)
        ok("phone unique check", taken is True)

    # CLEANUP
    async with async_session() as s:
        await s.execute(delete(Attachment).where(Attachment.report_id == report_id))
        await s.execute(delete(Report).where(Report.id == report_id))
        await s.execute(delete(User).where(User.telegram_id == test_tg))
        await s.commit()
    ok("CLEANUP", True)

    # 6. Locales — yangi kalit'lar
    print("\n[6] Locales")
    from bot.utils.i18n import t
    NEW_KEYS = [
        "report.intro", "report.ask_description", "report.too_short",
        "report.confirm", "report.confirm.send", "report.success",
        "report.feedback_type", "report.feedback_description",
        "report.back_done", "menu.back",
    ]
    for k in NEW_KEYS:
        val = t(k, "uz")
        ok(f"locale: {k}", val != k and len(val) > 0)

    # 7. Locale placeholder check
    print("\n[7] Locale placeholders")
    confirm_text = t("report.confirm", "uz",
                     type="Test", description="Test description",
                     full_name="Test", phone="+998901234567")
    ok(
        "report.confirm formati to'g'ri",
        "Test" in confirm_text and "+998901234567" in confirm_text and "[3/3]" in confirm_text,
    )

    intro_text = t("report.intro", "uz", name="Test User")
    ok(
        "report.intro [1/3] progress va name",
        "[1/3]" in intro_text and "Test User" in intro_text,
    )

    desc_text = t("report.ask_description", "uz")
    ok(
        "report.ask_description [2/3] + 5 savol",
        "[2/3]" in desc_text and "Qachon" in desc_text and "Qayerda" in desc_text,
    )

    too_short = t("report.too_short", "uz", count=5)
    ok("too_short count placeholder", "5" in too_short)

    # XULOSA
    total = len(results)
    passed = sum(1 for _, c, _ in results if c)
    failed = total - passed

    print("\n" + "=" * 64)
    print(f"  NATIJA: {passed}/{total} PASS  |  {failed} FAIL")
    print("=" * 64)

    if failed:
        print("\nMuvaffaqiyatsiz testlar:")
        for n, c, d in results:
            if not c:
                print(f"  - {n}: {d}")
        sys.exit(1)
    print("\n  Hammasi muvaffaqiyatli!")


if __name__ == "__main__":
    asyncio.run(main())
