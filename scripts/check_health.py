"""Loyiha holatini tekshirish."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


async def main() -> None:
    print("=== Himoya Bot Health Check ===\n")

    # 1. Config
    try:
        from config import settings
        print(f"[OK] Config yuklandi")
        print(f"     Bot: @{settings.bot_username}")
        print(f"     Env: {settings.environment}")
        print(f"     Adminlar: {len(settings.admin_ids)} ta")
    except Exception as e:
        print(f"[XATO] Config: {e}")
        sys.exit(1)

    # 2. DB
    try:
        from bot.database.db import init_db, async_session
        from bot.database.models import User, Report
        from sqlalchemy import select, func

        await init_db()
        async with async_session() as s:
            users = await s.scalar(select(func.count()).select_from(User))
            reports = await s.scalar(select(func.count()).select_from(Report))
        print(f"[OK] DB ishlamoqda")
        print(f"     Users: {users}, Reports: {reports}")
    except Exception as e:
        print(f"[XATO] DB: {e}")
        sys.exit(1)

    # 3. Telegram API
    try:
        from aiogram import Bot
        bot = Bot(token=settings.bot_token)
        me = await bot.get_me()
        print(f"[OK] Telegram API ishlamoqda")
        print(f"     Bot: @{me.username} (id={me.id})")
        await bot.session.close()
    except Exception as e:
        print(f"[XATO] Telegram: {e}")
        sys.exit(1)

    # 4. Locales
    try:
        from bot.utils.i18n import t
        for lang in ("uz", "ru", "en"):
            txt = t("start.welcome", lang)
            assert txt and txt != "start.welcome", f"{lang} tarjima topilmadi"
            print(f"[OK] Locale {lang}: {len(txt)} ta belgi")
    except Exception as e:
        print(f"[XATO] i18n: {e}")
        sys.exit(1)

    print("\n=== Hammasi tayyor! ===")


if __name__ == "__main__":
    asyncio.run(main())
