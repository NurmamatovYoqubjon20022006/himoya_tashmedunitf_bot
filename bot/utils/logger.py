"""Loguru logger sozlamalari."""
from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

from config import settings, BASE_DIR


def setup_logger() -> None:
    """Loguru'ni qayta sozlash: konsol + fayl."""
    logger.remove()

    logger.add(
        sys.stdout,
        level=settings.log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    log_dir: Path = BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    logger.add(
        log_dir / "bot_{time:YYYY-MM-DD}.log",
        level=settings.log_level,
        rotation="00:00",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
    )
