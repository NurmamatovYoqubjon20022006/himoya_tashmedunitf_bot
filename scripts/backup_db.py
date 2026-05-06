"""PostgreSQL DB backup (pg_dump).

Saqlash joyi: data/backups/himoya_YYYYMMDD_HHMMSS.dump
Format: PostgreSQL custom (-Fc) — siqilgan, pg_restore bilan tiklash mumkin.

Eslatma: data/backups/ .gitignore'da — git'ga TUSHMAYDI (maxfiy ma'lumot).

Tiklash:
  pg_restore -h localhost -U postgres -d himoya -c FILE.dump
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from config import settings  # noqa: E402

BACKUP_DIR = BASE_DIR / "data" / "backups"
RETAIN_LAST = 30  # so'nggi N ta backup'ni saqlash, qolgani avtomatik o'chiriladi


def find_pg_dump() -> str:
    """pg_dump'ni topish: PATH yoki Windows'dagi standart joydan."""
    found = shutil.which("pg_dump")
    if found:
        return found
    for candidate in [
        r"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe",
    ]:
        if Path(candidate).exists():
            return candidate
    raise FileNotFoundError(
        "pg_dump topilmadi. PostgreSQL'ni o'rnating yoki PATH'ga qo'shing."
    )


def parse_db_url(url: str) -> dict[str, str]:
    """SQLAlchemy URL'idan host/port/db/user/password ajratib olish."""
    cleaned = re.sub(r"^postgresql\+\w+://", "postgresql://", url)
    p = urlparse(cleaned)
    return {
        "host": p.hostname or "localhost",
        "port": str(p.port or 5432),
        "user": p.username or "postgres",
        "password": p.password or "",
        "dbname": p.path.lstrip("/") or "himoya",
    }


def cleanup_old(directory: Path, keep: int) -> int:
    """Eski backuplarni o'chirish — so'nggi `keep` tasini saqlash."""
    files = sorted(
        directory.glob("himoya_*.dump"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    removed = 0
    for old in files[keep:]:
        old.unlink()
        removed += 1
    return removed


def main() -> None:
    pg_dump = find_pg_dump()
    cfg = parse_db_url(settings.database_sync_url)

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = BACKUP_DIR / f"himoya_{stamp}.dump"

    cmd = [
        pg_dump,
        "-h", cfg["host"],
        "-p", cfg["port"],
        "-U", cfg["user"],
        "-d", cfg["dbname"],
        "-F", "c",                # custom format (siqilgan)
        "-Z", "9",                # max compression
        "--no-owner",
        "--no-privileges",
        "-f", str(target),
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = cfg["password"]

    print(f"Backup boshlanmoqda: {cfg['user']}@{cfg['host']}:{cfg['port']}/{cfg['dbname']}")
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"XATO: {result.stderr}", file=sys.stderr)
        if target.exists():
            target.unlink()
        sys.exit(1)

    size_mb = target.stat().st_size / (1024 * 1024)
    print(f"✅ Backup yaratildi: {target}")
    print(f"   Hajmi: {size_mb:.2f} MB")

    removed = cleanup_old(BACKUP_DIR, RETAIN_LAST)
    if removed:
        print(f"   Eski {removed} ta backup o'chirildi (so'nggi {RETAIN_LAST} ta saqlandi)")


if __name__ == "__main__":
    main()
