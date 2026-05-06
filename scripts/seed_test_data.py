"""Yangi formatda — to'liq test foydalanuvchilar va murojaatlar.

Yaratiladi:
  - 5 ta to'liq registratsiya qilingan test foydalanuvchi (talaba, magistr, o'qituvchi, xodim)
  - 8 ta turli holatdagi test murojaat (har xil status va incident_type)
  - 1 ta admin (admin / Admin1234!)
"""
from __future__ import annotations

import asyncio
import secrets
import string
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import asyncpg  # noqa: E402
import bcrypt  # noqa: E402

from config import settings  # noqa: E402

# .env'dan oladi (asyncpg DRIVER siz, plain postgresql://)
DB_URL = settings.database_sync_url.replace("postgresql+psycopg://", "postgresql://")


def gen_tracking() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "H-" + "".join(secrets.choice(alphabet) for _ in range(8))


async def main() -> None:
    conn = await asyncpg.connect(DB_URL)

    # ───── 1. Test foydalanuvchilar (to'liq registratsiya) ─────
    USERS = [
        {
            "telegram_id": 100_000_001,
            "username": "malika_yusupova",
            "phone": "+998901112201",
            "full_name": "Malika Yusupova Akmalovna",
            "user_type": "STUDENT",
            "faculty": "DAVOLASH_1",
            "course": 3,
            "direction": "Davolash ishi",
            "group_name": "301-A",
        },
        {
            "telegram_id": 100_000_002,
            "username": "zulfiya_rahimova",
            "phone": "+998901112202",
            "full_name": "Zulfiya Rahimova Bakhtiyorovna",
            "user_type": "STUDENT",
            "faculty": "PEDIATRIYA",
            "course": 2,
            "direction": "Pediatriya",
            "group_name": "205-B",
        },
        {
            "telegram_id": 100_000_003,
            "username": "nodira_hasanova",
            "phone": "+998901112203",
            "full_name": "Nodira Hasanova Sherzodovna",
            "user_type": "STUDENT",
            "faculty": "DAVOLASH_2",
            "course": 4,
            "direction": "Davolash ishi (sirtqi)",
            "group_name": "402-V",
        },
        {
            "telegram_id": 100_000_004,
            "username": "aziz_karimov",
            "phone": "+998901112204",
            "full_name": "Aziz Karimov Olimovich",
            "user_type": "MASTER",
            "faculty": "PEDIATRIYA",
            "course": 1,
            "direction": "Bolalar reanimatologiyasi",
            "group_name": "M-101",
        },
        {
            "telegram_id": 100_000_005,
            "username": "shahnoza_t",
            "phone": "+998901112205",
            "full_name": "Shahnoza Tursunova Erkinovna",
            "user_type": "TEACHER",
            "faculty": "DAVOLASH_1",
            "course": None,
            "direction": None,
            "group_name": None,
            "position": "Kafedra dotsenti",
        },
        {
            "telegram_id": 100_000_006,
            "username": "jamshid_xodim",
            "phone": "+998901112206",
            "full_name": "Jamshid Boboyev Anvarovich",
            "user_type": "STAFF",
            "faculty": None,
            "course": None,
            "direction": None,
            "group_name": None,
            "position": "Kutubxona xodimi",
        },
    ]

    for u in USERS:
        await conn.execute(
            """
            INSERT INTO users (
                telegram_id, username, language, role,
                phone, full_name, user_type, faculty, course,
                direction, group_name, position,
                is_blocked, is_registered, registered_at
            ) VALUES (
                $1, $2, 'uz', 'USER',
                $3, $4, $5, $6, $7,
                $8, $9, $10,
                false, true, NOW()
            )
            ON CONFLICT (telegram_id) DO UPDATE SET
                phone=EXCLUDED.phone,
                full_name=EXCLUDED.full_name,
                user_type=EXCLUDED.user_type,
                faculty=EXCLUDED.faculty,
                course=EXCLUDED.course,
                direction=EXCLUDED.direction,
                group_name=EXCLUDED.group_name,
                position=EXCLUDED.position,
                is_registered=true
            """,
            u["telegram_id"], u["username"], u["phone"], u["full_name"],
            u["user_type"], u["faculty"], u.get("course"),
            u.get("direction"), u.get("group_name"), u.get("position"),
        )

    user_rows = await conn.fetch(
        "SELECT id, telegram_id, full_name FROM users ORDER BY id"
    )
    user_id_by_tg = {r["telegram_id"]: r["id"] for r in user_rows}

    # ───── 2. Test murojaatlar ─────
    REPORTS = [
        {
            "tg": 100_000_001,
            "incident_type": "HARASSMENT",
            "description": "O'qituvchi dars paytida noqulay so'zlar ishlatdi va talabani uyaltirdi. "
                           "Vaziyat 5 daqiqa davom etdi va guruh oldida edi.",
            "location": "3-korpus, 201-xona",
            "incident_date": "2026-04-10",
            "status": "NEW",
        },
        {
            "tg": 100_000_002,
            "incident_type": "PRESSURE",
            "description": "Dekanat xodimi imtihon bahosi uchun moddiy talab qildi. "
                           "Qo'rqitish va shantaj holatlari kuzatildi.",
            "location": "Dekanat binosi, 1-qavat",
            "incident_date": "2026-04-15",
            "status": "IN_REVIEW",
        },
        {
            "tg": 100_000_003,
            "incident_type": "DISCRIMINATION",
            "description": "O'qituvchi guruh oldida talabani millati uchun kamsitdi. "
                           "Bir necha bor takrorlandi.",
            "location": "1-korpus, 105-xona",
            "incident_date": "2026-04-20",
            "status": "RESOLVED",
            "admin_note": "\n— Komissiya: Tergov o'tkazildi, choralar ko'rildi.",
        },
        {
            "tg": 100_000_001,
            "incident_type": "VIOLENCE",
            "description": "Koridorda jismoniy zo'ravonlik holati sodir bo'ldi. "
                           "Talaba boshqa talaba tomonidan urilgan.",
            "location": "Kutubxona yonida, 2-qavat",
            "incident_date": "2026-04-22",
            "status": "RESOLVED",
            "admin_note": "\n— Komissiya: Politsiyaga xabar berildi.",
        },
        {
            "tg": 100_000_004,
            "incident_type": "PRESSURE",
            "description": "Magistratura ilmiy rahbari ortiqcha vazifalar yuklamoqda va "
                           "oz vaqtda tugatishni talab qilmoqda.",
            "location": "Kafedra xonasi, 3-qavat",
            "incident_date": "2026-04-25",
            "status": "IN_REVIEW",
        },
        {
            "tg": 100_000_002,
            "incident_type": "OTHER",
            "description": "Talabalar guruhchasida o'qituvchi tomonidan shaxsiy "
                           "ma'lumotlar tarqatildi va kamsituvchi gaplar yozildi.",
            "location": "Telegram guruh",
            "incident_date": "2026-05-01",
            "status": "NEW",
        },
        {
            "tg": 100_000_006,
            "incident_type": "HARASSMENT",
            "description": "Ish vaqtida hamkasb tomonidan nojo'ya munosabat ko'rsatildi. "
                           "Bir necha marta takrorlandi va guvohlar bor.",
            "location": "Kutubxona, 1-qavat",
            "incident_date": "2026-04-28",
            "status": "NEW",
        },
        {
            "tg": 100_000_003,
            "incident_type": "DISCRIMINATION",
            "description": "Stipendiya taqsimotida adolatsiz munosabat kuzatildi. "
                           "Yuqori bahoga qaramay stipendiyadan foydalanmadim.",
            "location": "Moliya bo'limi",
            "incident_date": "2026-04-30",
            "status": "REJECTED",
            "admin_note": "\n— Komissiya: Hujjatlar tekshirildi, holat asossiz topildi.",
        },
    ]

    for rep in REPORTS:
        tid = gen_tracking()
        # Unique tracking_id ni ta'minlash
        while await conn.fetchval(
            "SELECT 1 FROM reports WHERE tracking_id=$1", tid
        ):
            tid = gen_tracking()

        user_id = user_id_by_tg.get(rep["tg"])
        await conn.execute(
            """
            INSERT INTO reports (
                tracking_id, user_id, incident_type, description,
                location, incident_date, status, admin_note, is_anonymous
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, false)
            """,
            tid, user_id, rep["incident_type"], rep["description"],
            rep["location"], rep["incident_date"], rep["status"],
            rep.get("admin_note"),
        )

    # ───── 3. Admin (yoki yangilash) ─────
    pw_hash = bcrypt.hashpw(b"Admin1234!", bcrypt.gensalt(12)).decode()
    await conn.execute(
        """
        INSERT INTO admin_users (username, password_hash, full_name, role, is_active)
        VALUES ($1, $2, 'Super Admin', 'admin', true)
        ON CONFLICT (username) DO UPDATE SET password_hash=$2
        """,
        "admin", pw_hash,
    )

    # ───── 4. Yakuniy hisobot ─────
    u = await conn.fetchval("SELECT COUNT(*) FROM users")
    r = await conn.fetchval("SELECT COUNT(*) FROM reports")
    a = await conn.fetchval("SELECT COUNT(*) FROM attachments")
    ad = await conn.fetchval("SELECT COUNT(*) FROM admin_users")
    reg = await conn.fetchval("SELECT COUNT(*) FROM users WHERE is_registered")
    with_phone = await conn.fetchval("SELECT COUNT(*) FROM users WHERE phone IS NOT NULL")

    print()
    print("=" * 60)
    print("  Test ma'lumotlar yaratildi")
    print("=" * 60)
    print(f"  👥 Foydalanuvchilar:      {u} (registered: {reg}, phone: {with_phone})")
    print(f"  📋 Murojaatlar:           {r}")
    print(f"  📎 Ilovalar:              {a}")
    print(f"  👮 Adminlar:              {ad}")
    print()
    print("  🔑 Admin login: admin / Admin1234!")
    print("  🌐 Web panel: http://localhost:3000/login")
    print("=" * 60)

    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
