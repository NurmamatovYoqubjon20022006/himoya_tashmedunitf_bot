"""PostgreSQL'da `himoya` ma'lumotlar bazasini yaratish.

Foydalanuvchi va parolni .env'dan oladi. Agar DB allaqachon mavjud bo'lsa,
hech narsa qilmaydi. Aks holda CREATE DATABASE qiladi.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import asyncpg  # noqa: E402
from urllib.parse import urlparse  # noqa: E402

from config import settings  # noqa: E402


async def main() -> None:
    parsed = urlparse(settings.database_url.replace("+asyncpg", ""))
    user = parsed.username or "postgres"
    password = parsed.password or ""
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432
    db_name = (parsed.path or "/himoya").lstrip("/")

    print(f"[*] Server: {host}:{port}, user={user}, target DB={db_name}")

    try:
        conn = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database="postgres",
        )
    except Exception as e:
        print(f"[XATO] postgres'ga ulana olmadim: {e}")
        print("       .env'dagi DATABASE_URL/parolni tekshiring.")
        sys.exit(1)

    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname=$1", db_name
        )
        if exists:
            print(f"[OK] '{db_name}' DB allaqachon mavjud.")
        else:
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            print(f"[OK] '{db_name}' DB yaratildi.")
    finally:
        await conn.close()

    # Tablalarni yaratish
    from bot.database.db import init_db
    await init_db()
    print("[OK] Jadvallar yaratildi (users, reports, attachments).")


if __name__ == "__main__":
    asyncio.run(main())
