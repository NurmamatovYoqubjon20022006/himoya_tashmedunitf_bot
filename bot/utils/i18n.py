"""Oddiy i18n — locales/{lang}.json fayllari."""
from __future__ import annotations

import json
from pathlib import Path

from config import BASE_DIR

_cache: dict[str, dict[str, str]] = {}


def _load(lang: str) -> dict[str, str]:
    if lang in _cache:
        return _cache[lang]
    path: Path = BASE_DIR / "locales" / f"{lang}.json"
    if not path.exists():
        _cache[lang] = {}
        return _cache[lang]
    _cache[lang] = json.loads(path.read_text(encoding="utf-8"))
    return _cache[lang]


def t(key: str, lang: str = "uz", **kwargs) -> str:
    """Tarjima olish. Topilmasa key qaytariladi."""
    text = _load(lang).get(key) or _load("uz").get(key) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
