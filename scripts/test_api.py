"""
To'liq API test skripti — NextAuth v5 bilan.
Ishlatish: python scripts/test_api.py
Oldin: cd web && npm start  (yoki ishga tushib turgan bo'lishi kerak)
"""
import asyncio
import http.cookiejar
import json
import sys
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

# .env'dan DB credentials olish (kodga yashirib qo'ymaslik uchun)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import settings  # noqa: E402

DB_URL_PLAIN = settings.database_sync_url.replace("postgresql+psycopg://", "postgresql://")
DB_URL_ASYNCPG = settings.database_url

BASE = "http://localhost:3000"
results: list[tuple[str, str, str]] = []


def ok(name: str, cond: bool, detail: str = "") -> None:
    status = "PASS" if cond else "FAIL"
    results.append((name, status, detail))
    mark = "[PASS]" if cond else "[FAIL]"
    print(f"  {mark} {name}" + (f" — {detail}" if detail else ""))


# ── Session bilan opener ─────────────────────────────────────────────────────
def make_opener() -> urllib.request.OpenerDirector:
    jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(jar),
        urllib.request.HTTPRedirectHandler(),
    )


def api(opener: urllib.request.OpenerDirector, method: str, path: str,
        body: dict | None = None) -> tuple[int, dict | str]:
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with opener.open(req, timeout=10) as r:
            raw = r.read().decode()
            try:
                return r.status, json.loads(raw)
            except json.JSONDecodeError:
                return r.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, raw


def login(opener: urllib.request.OpenerDirector) -> bool:
    """NextAuth v5 credentials login. Cookie jar'da session-token paydo bo'lishini tekshiramiz."""
    # 1. CSRF token ol (cookie ham qo'shiladi)
    try:
        with opener.open(f"{BASE}/api/auth/csrf", timeout=10) as r:
            csrf_data = json.loads(r.read())
            csrf_token = csrf_data.get("csrfToken", "")
    except Exception as e:
        print(f"  [WARN] CSRF xato: {e}")
        return False

    # 2. POST /api/auth/callback/credentials (form-urlencoded, redirect ham OK)
    payload = urllib.parse.urlencode({
        "username": "admin",
        "password": "Admin1234!",
        "csrfToken": csrf_token,
        "callbackUrl": f"{BASE}/dashboard",
    }).encode()

    try:
        req = urllib.request.Request(
            f"{BASE}/api/auth/callback/credentials",
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        opener.open(req, timeout=10).read()
    except urllib.error.HTTPError:
        pass
    except Exception as e:
        print(f"  [WARN] Login xato: {e}")
        return False

    # 3. Cookie jar'da session-token paydo bo'lganmi?
    for handler in opener.handlers:
        if isinstance(handler, urllib.request.HTTPCookieProcessor):
            for c in handler.cookiejar:
                if "session-token" in c.name:
                    return True
    return False


# ── Asosiy test ──────────────────────────────────────────────────────────────
async def run_tests() -> None:
    print("\n" + "=" * 60)
    print("  HIMOYA BOT — TO'LIQ API TEST")
    print("=" * 60)

    # ── 1. PostgreSQL ─────────────────────────────────────────────
    print("\n[1] PostgreSQL ulanish testi")
    try:
        import asyncpg
        conn = await asyncpg.connect(
            DB_URL_PLAIN
        )
        u   = await conn.fetchval("SELECT COUNT(*) FROM users")
        r   = await conn.fetchval("SELECT COUNT(*) FROM reports")
        a   = await conn.fetchval("SELECT COUNT(*) FROM admin_users")
        att = await conn.fetchval("SELECT COUNT(*) FROM attachments")
        await conn.close()
        ok("DB ulanish", True, f"users={u}, reports={r}, attachments={att}, admins={a}")
        ok("Test ma'lumotlar mavjud", r > 0, f"{r} ta murojaat")
        ok("Admin mavjud", a > 0, f"{a} ta admin")
    except Exception as e:
        ok("DB ulanish", False, str(e))
        _print_summary(); return

    # ── 2. Bot modellari ─────────────────────────────────────────
    print("\n[2] Python bot modellari testi")
    try:
        sys.path.insert(0, ".")
        from bot.database.models import UserRole, ReportStatus, IncidentType
        ok("Bot modellari import", True)
        ok("UserRole ENUM", len(list(UserRole)) >= 5)
        ok("ReportStatus ENUM", len(list(ReportStatus)) >= 4)
        ok("IncidentType ENUM", len(list(IncidentType)) >= 5)
    except Exception as e:
        ok("Bot modellari import", False, str(e))

    # ── 3. SQLAlchemy ulanish ────────────────────────────────────
    print("\n[3] Bot SQLAlchemy ulanish testi")
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        engine = create_async_engine(
            DB_URL_ASYNCPG,
            echo=False,
        )
        async with engine.connect() as c:
            count = (await c.execute(text("SELECT COUNT(*) FROM reports"))).scalar()
        await engine.dispose()
        ok("SQLAlchemy async ulanish", True, f"{count} ta report")
    except Exception as e:
        ok("SQLAlchemy async ulanish", False, str(e))

    # ── 4. Next.js server ────────────────────────────────────────
    print("\n[4] Next.js server testi")
    anon = make_opener()
    try:
        with anon.open(f"{BASE}/login", timeout=5) as r:
            ok("Next.js server ishlamoqda", r.status == 200, f"HTTP {r.status}")
    except Exception as e:
        ok("Next.js server ishlamoqda", False, str(e))
        print("  [WARN] Server ishlamayapti — cd web && npm start")
        _print_summary(); return

    # ── 5. Auth ──────────────────────────────────────────────────
    print("\n[5] Auth API testi")
    try:
        with anon.open(f"{BASE}/api/auth/csrf", timeout=5) as r:
            d = json.loads(r.read())
            ok("CSRF endpoint", "csrfToken" in d)
    except Exception as e:
        ok("CSRF endpoint", False, str(e))

    # Auth session qurish
    sess = make_opener()
    logged_in = login(sess)
    ok("Login (admin / Admin1234!)", logged_in, "session cookie olindi" if logged_in else "xato")

    # Agar login bo'lmasa, anonymous opener bilan test qil (auth xatolarini ko'rish)
    active = sess if logged_in else anon

    # ── 6. Reports CRUD ──────────────────────────────────────────
    print("\n[6] Reports API — CRUD testi")

    code, data = api(active, "GET", "/api/reports")
    if logged_in:
        ok("GET /api/reports", code == 200 and isinstance(data, dict) and "reports" in data,
           f"total={data.get('total',0) if isinstance(data,dict) else ''}")
        ok("Reports pagination", isinstance(data, dict) and "page" in data and "limit" in data)
    else:
        ok("GET /api/reports", code == 401, f"HTTP {code} (auth kerak)")

    code, data = api(active, "GET", "/api/reports?status=NEW")
    if logged_in:
        ok("GET /api/reports?status=NEW", code == 200 and isinstance(data, dict),
           f"{data.get('total',0) if isinstance(data,dict) else ''} ta")
    else:
        ok("GET /api/reports?status=NEW", code == 401, f"HTTP {code}")

    code, data = api(active, "GET", "/api/reports/1")
    if logged_in:
        ok("GET /api/reports/1 (detail)", code == 200 and isinstance(data, dict) and "tracking_id" in data,
           f"tracking_id={data.get('tracking_id') if isinstance(data,dict) else ''}")
    else:
        ok("GET /api/reports/1", code == 401, f"HTTP {code}")

    code, data = api(active, "PATCH", "/api/reports/1",
                     {"status": "IN_REVIEW", "admin_note": "Test izohi"})
    if logged_in:
        ok("PATCH /api/reports/1 (holat o'zgartirish)",
           code == 200 and isinstance(data, dict) and data.get("status") == "IN_REVIEW",
           f"status={data.get('status') if isinstance(data,dict) else ''}")
    else:
        ok("PATCH /api/reports/1", code == 401, f"HTTP {code}")

    # Restore status
    if logged_in:
        api(active, "PATCH", "/api/reports/1", {"status": "NEW", "admin_note": None})

    # ── 7. Stats ─────────────────────────────────────────────────
    print("\n[7] Stats API testi")
    code, data = api(active, "GET", "/api/stats")
    if logged_in:
        ok("GET /api/stats", code == 200 and isinstance(data, dict) and "stats" in data)
        if isinstance(data, dict):
            ok("Stats.total", isinstance(data.get("stats", {}).get("total"), int),
               f"total={data.get('stats',{}).get('total')}")
            ok("byIncidentType", isinstance(data.get("byIncidentType"), list))
            ok("last7Days", isinstance(data.get("last7Days"), list))
            ok("recentReports", isinstance(data.get("recentReports"), list))
    else:
        ok("GET /api/stats", code == 401, f"HTTP {code}")

    # ── 8. Users ─────────────────────────────────────────────────
    print("\n[8] Users API testi")
    code, data = api(active, "GET", "/api/users")
    if logged_in:
        ok("GET /api/users", code == 200 and isinstance(data, dict) and "users" in data,
           f"total={data.get('total',0) if isinstance(data,dict) else ''}")
    else:
        ok("GET /api/users", code == 401, f"HTTP {code}")

    code, data = api(active, "GET", "/api/users?search=malika")
    if logged_in:
        ok("GET /api/users?search=malika", code == 200 and isinstance(data, dict))
    else:
        ok("GET /api/users?search=malika", code == 401, f"HTTP {code}")

    # ── 9. Admins CRUD ───────────────────────────────────────────
    print("\n[9] Admins API — CRUD testi")
    code, data = api(active, "GET", "/api/admins")
    if logged_in:
        ok("GET /api/admins", code == 200 and isinstance(data, dict) and "admins" in data,
           f"{len(data.get('admins',[])) if isinstance(data,dict) else 0} ta admin")
    else:
        ok("GET /api/admins", code == 401, f"HTTP {code}")

    new_admin = {
        "username": "test_yangi_admin",
        "full_name": "Test Yangi Admin",
        "password": "TestPass456!",
        "role": "commission",
    }
    code, data = api(active, "POST", "/api/admins", new_admin)
    if logged_in:
        ok("POST /api/admins (yangi admin yaratish)",
           code in (201, 409),
           f"HTTP {code} — id={data.get('id') if isinstance(data,dict) else data}")
    else:
        ok("POST /api/admins", code == 401, f"HTTP {code}")

    # ── 10. Auth himoya ──────────────────────────────────────────
    print("\n[10] Auth himoya testi (session bo'lmasdan)")
    for path in ["/api/reports", "/api/stats", "/api/users", "/api/admins"]:
        code2, _ = api(anon, "GET", path)
        ok(f"Auth himoya {path}", code2 == 401, f"HTTP {code2}")

    # ── 11. E2E murojaat yaratish (DB orqali) ───────────────────
    print("\n[11] E2E: Murojaat yaratish va o'qish testi")
    try:
        import asyncpg
        conn2 = await asyncpg.connect(
            DB_URL_PLAIN
        )
        # Yagona tracking_id bilan test murojaat
        import random, string
        tid = "E2E-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        await conn2.execute("""
            INSERT INTO reports
              (tracking_id, incident_type, description, location, status, is_anonymous)
            VALUES ($1, 'HARASSMENT', 'E2E test murojaat', 'Test joy', 'NEW', true)
        """, tid)
        row = await conn2.fetchrow("SELECT * FROM reports WHERE tracking_id=$1", tid)
        ok("E2E murojaat yaratish (DB)", row is not None, f"tracking_id={tid}")
        ok("E2E status NEW", row["status"] == "NEW")

        await conn2.execute(
            "UPDATE reports SET status='RESOLVED', admin_note='Hal etildi' WHERE tracking_id=$1", tid
        )
        updated = await conn2.fetchrow("SELECT status, admin_note FROM reports WHERE tracking_id=$1", tid)
        ok("E2E murojaat yangilash", updated["status"] == "RESOLVED")
        ok("E2E admin_note saqlash", updated["admin_note"] == "Hal etildi")

        await conn2.execute("DELETE FROM reports WHERE tracking_id=$1", tid)
        deleted = await conn2.fetchrow("SELECT id FROM reports WHERE tracking_id=$1", tid)
        ok("E2E murojaat o'chirish", deleted is None)
        await conn2.close()
    except Exception as e:
        ok("E2E DB test", False, str(e))

    _print_summary()


def _print_summary() -> None:
    total  = len(results)
    passed = sum(1 for _, s, _ in results if s == "PASS")
    failed = total - passed
    print("\n" + "=" * 60)
    print(f"  NATIJA: {passed}/{total} PASS  |  {failed} FAIL")
    print("=" * 60)
    if failed:
        print("\n  Muvaffaqiyatsiz testlar:")
        for name, status, detail in results:
            if status == "FAIL":
                print(f"    - {name}: {detail}")
    else:
        print("\n  Barcha testlar muvaffaqiyatli!")
    print()


if __name__ == "__main__":
    asyncio.run(run_tests())
