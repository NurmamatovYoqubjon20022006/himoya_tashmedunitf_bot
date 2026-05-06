"""Yangi maydonlar (phone, faculty, user_type, course, direction)
web API javobida ko'rinishini tekshiramiz."""
from __future__ import annotations

import asyncio
import http.cookiejar
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import settings  # noqa: E402

DB_URL_PLAIN = settings.database_sync_url.replace("postgresql+psycopg://", "postgresql://")

BASE = "http://localhost:3000"


def make_opener():
    jar = http.cookiejar.CookieJar()
    return jar, urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(jar),
        urllib.request.HTTPRedirectHandler(),
    )


def login(opener, jar) -> bool:
    with opener.open(f"{BASE}/api/auth/csrf", timeout=10) as r:
        csrf = json.loads(r.read())["csrfToken"]
    payload = urllib.parse.urlencode({
        "username": "admin",
        "password": "Admin1234!",
        "csrfToken": csrf,
        "callbackUrl": f"{BASE}/dashboard",
    }).encode()
    req = urllib.request.Request(
        f"{BASE}/api/auth/callback/credentials",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        opener.open(req, timeout=10).read()
    except urllib.error.HTTPError:
        pass
    return any("session-token" in c.name for c in jar)


def api_get(opener, path: str):
    req = urllib.request.Request(BASE + path)
    try:
        with opener.open(req, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


async def main() -> None:
    print("=" * 60)
    print("  YANGI MAYDONLAR — API JAVOBIDA TEKSHIRUV")
    print("=" * 60)

    # Test foydalanuvchini DB orqali yaratamiz
    import asyncpg
    import secrets
    test_phone = "+99890" + str(secrets.randbelow(10_000_000)).zfill(7)
    test_tg = 999_900_000 + secrets.randbelow(99_999)

    conn = await asyncpg.connect(DB_URL_PLAIN)
    await conn.execute("""
        INSERT INTO users (
            telegram_id, username, language, role, phone, full_name,
            user_type, faculty, course, direction, group_name,
            is_blocked, is_registered, registered_at
        ) VALUES (
            $1, 'test_new_fields', 'uz', 'USER', $2, 'API Test User',
            'STUDENT', 'PEDIATRIYA', 3, 'Pediatriya yo''nalishi', '301-A',
            false, true, NOW()
        )
    """, test_tg, test_phone)
    user_id = await conn.fetchval(
        "SELECT id FROM users WHERE telegram_id=$1", test_tg
    )
    # Yangi report — random tracking_id
    tid = "NF-" + "".join([str(secrets.randbelow(10)) for _ in range(6)])
    await conn.execute("""
        INSERT INTO reports (
            tracking_id, user_id, incident_type, description,
            location, status, is_anonymous
        ) VALUES (
            $1, $2, 'HARASSMENT', 'Test report for new fields',
            'Test joy', 'NEW', false
        )
    """, tid, user_id)
    report_id = await conn.fetchval(
        "SELECT id FROM reports WHERE tracking_id=$1", tid
    )
    await conn.close()
    print(f"  [SETUP] Test user yaratildi (id={user_id}, phone={test_phone})")
    print(f"  [SETUP] Test report yaratildi (id={report_id})")

    jar, opener = make_opener()
    if not login(opener, jar):
        print("  [FAIL] Login xato")
        sys.exit(1)
    print("  [PASS] Login OK\n")

    # 1. /api/users — yangi maydonlar bormi?
    code, data = api_get(opener, "/api/users?search=" + urllib.parse.quote("API Test"))
    if code == 200 and data["users"]:
        u = data["users"][0]
        required = ["phone", "user_type", "faculty", "course", "direction", "group_name", "is_registered"]
        missing = [k for k in required if k not in u]
        if missing:
            print(f"  [FAIL] /api/users — yetishmayotgan maydon: {missing}")
        else:
            print(f"  [PASS] /api/users — barcha yangi maydon bor")
            print(f"         phone={u['phone']}, user_type={u['user_type']}, "
                  f"faculty={u['faculty']}, course={u['course']}")
    else:
        print(f"  [FAIL] /api/users qaytmadi: {code}")

    # 2. /api/reports/{id} — user yangi maydonlar bilan
    code, data = api_get(opener, f"/api/reports/{report_id}")
    if code == 200 and "user" in data and data["user"]:
        u = data["user"]
        required = ["phone", "user_type", "faculty", "course", "direction"]
        missing = [k for k in required if k not in u]
        if missing:
            print(f"  [FAIL] /api/reports/[id].user — yetishmayotgan: {missing}")
        else:
            print(f"  [PASS] /api/reports/[id].user — barcha yangi maydon bor")
            print(f"         phone={u['phone']}, full_name={u['full_name']}, "
                  f"faculty={u['faculty']}")
    else:
        print(f"  [FAIL] /api/reports/[id] qaytmadi: {code}")

    # 3. /api/reports — user select'da nimalar?
    code, data = api_get(opener, "/api/reports?limit=5")
    if code == 200 and data["reports"]:
        r0 = data["reports"][0]
        if "user" in r0:
            print(f"  [INFO] /api/reports — user keys: {list(r0['user'].keys()) if r0['user'] else 'None'}")
        else:
            print(f"  [WARN] /api/reports — user maydoni yo'q")

    # CLEANUP
    conn = await asyncpg.connect(DB_URL_PLAIN)
    await conn.execute("DELETE FROM reports WHERE id=$1", report_id)
    await conn.execute("DELETE FROM users WHERE id=$1", user_id)
    await conn.close()
    print("\n  [CLEANUP] Test ma'lumotlari o'chirildi")


if __name__ == "__main__":
    asyncio.run(main())
