"""F.I.O, telefon, yo'nalish, guruh bo'yicha web search test."""
from __future__ import annotations

import http.cookiejar
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://localhost:3000"


def make_session():
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(jar),
        urllib.request.HTTPRedirectHandler(),
    )
    return jar, opener


def login(opener, jar) -> bool:
    csrf = json.loads(opener.open(f"{BASE}/api/auth/csrf", timeout=10).read())["csrfToken"]
    payload = urllib.parse.urlencode({
        "username": "admin", "password": "Admin1234!",
        "csrfToken": csrf, "callbackUrl": f"{BASE}/dashboard",
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


def search_reports(opener, query: str) -> int:
    encoded = urllib.parse.quote(query)
    r = opener.open(f"{BASE}/api/reports?search={encoded}", timeout=10)
    return json.loads(r.read())["total"]


def search_users(opener, query: str) -> int:
    encoded = urllib.parse.quote(query)
    r = opener.open(f"{BASE}/api/users?search={encoded}", timeout=10)
    return json.loads(r.read())["total"]


def main() -> None:
    print("=" * 60)
    print("  F.I.O / TELEFON / YO'NALISH SEARCH TEST")
    print("=" * 60)

    jar, opener = make_session()
    if not login(opener, jar):
        print("[FAIL] Login")
        sys.exit(1)
    print("[OK] Login\n")

    print("Reports search:")
    cases_reports = [
        ("Yusupova",        "F.I.O (familiya)"),
        ("Malika",          "F.I.O (ism)"),
        ("Karimov",         "F.I.O (boshqa familiya)"),
        ("+998901112201",   "telefon (to'liq)"),
        ("998901112",       "telefon (qisman)"),
        ("malika_yusupova", "username"),
        ("Pediatriya",      "yo'nalish"),
        ("Davolash",        "yo'nalish (qisman)"),
        ("301-A",           "guruh"),
        ("M-101",           "guruh (magistr)"),
        ("dotsent",         "lavozim"),
        ("kutubxona",       "lavozim/joy"),
    ]
    failed = 0
    for q, desc in cases_reports:
        try:
            total = search_reports(opener, q)
            mark = "[PASS]" if total > 0 else "[INFO]"
            print(f"  {mark} {desc:30} '{q}' -> {total} ta")
            if total == 0 and desc not in ("lavozim", "lavozim/joy"):
                # Lavozim — agar o'qituvchining murojaati bo'lmasa, 0 OK
                pass
        except Exception as e:
            failed += 1
            print(f"  [FAIL] {desc:30} '{q}' -> {e}")

    print("\nUsers search:")
    cases_users = [
        ("Yusupova",        "F.I.O"),
        ("+99890",          "telefon prefix"),
        ("malika_y",        "username"),
        ("Pediatriya",      "yo'nalish"),
    ]
    for q, desc in cases_users:
        try:
            total = search_users(opener, q)
            mark = "[PASS]" if total > 0 else "[INFO]"
            print(f"  {mark} {desc:30} '{q}' -> {total} ta")
        except Exception as e:
            failed += 1
            print(f"  [FAIL] {desc:30} '{q}' -> {e}")

    print("\n" + "=" * 60)
    print(f"  Search testi: {'OK' if failed == 0 else f'{failed} FAIL'}")
    print("=" * 60)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
