"""SQLite DB backup."""
from __future__ import annotations

import shutil
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "data" / "himoya.db"
BACKUP_DIR = BASE_DIR / "data" / "backups"


def main() -> None:
    if not DB_FILE.exists():
        print(f"DB topilmadi: {DB_FILE}")
        sys.exit(1)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = BACKUP_DIR / f"himoya_{timestamp}.db"
    shutil.copy2(DB_FILE, target)
    print(f"Backup yaratildi: {target}")


if __name__ == "__main__":
    main()
