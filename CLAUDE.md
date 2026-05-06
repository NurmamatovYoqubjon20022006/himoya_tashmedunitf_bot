# Himoya — TashMedUni Telegram Bot

## Loyiha haqida (Project)

Toshkent davlat tibbiyot universiteti Termiz filiali (TDTU Termiz filiali) uchun Telegram bot. Oliy ta'lim, fan va innovatsiyalar vazirligining **2026-yil 20-apreldagi 150-sonli buyrug'i** asosida yaratilgan.

**Maqsad:** Ta'lim muassasalarida o'quvchi-talaba qizlar va xotin-qizlar o'rtasida shilqimlik (harassment), tazyiq va zo'ravonlik holatlarining oldini olish, anonim murojaat qabul qilish, huquqiy yordam va psixologik ko'mak ko'rsatish.

**Bot:** [@himoya_tashmedunitf_bot](https://t.me/himoya_tashmedunitf_bot)

## Tech Stack

- **Python:** 3.14.3
- **Framework:** aiogram 3.x (async Telegram Bot API)
- **Database:** SQLite (aiosqlite) — kichik miqyos uchun yetarli, keyin PostgreSQL'ga o'tish mumkin
- **Storage:** Redis (FSM uchun, optional) yoki MemoryStorage
- **Config:** python-dotenv + pydantic-settings
- **Logging:** loguru
- **i18n:** Uzbek (default), Russian, English

## Folder tuzilishi

```
himoya_tashmedunitf_bot/
├── bot/
│   ├── handlers/      # Telegram message/callback handlers
│   ├── keyboards/     # Inline & reply keyboards
│   ├── states/        # FSM states (FSMContext)
│   ├── filters/       # Custom filters (admin, user role, etc.)
│   ├── middlewares/   # Throttling, i18n, db session, logging
│   ├── services/      # Business logic (report, notification, etc.)
│   ├── database/      # Models, queries, migrations
│   └── utils/         # Helpers (formatters, validators)
├── data/              # SQLite DB, uploaded files, attachments
├── logs/              # Bot log files
├── locales/           # uz/ru/en translations
├── docs/              # Documentation, 150-son buyruq matni
├── scripts/           # Admin scripts (backup, migrate, seed)
├── tests/             # pytest unit & integration tests
├── .env               # Secrets (NEVER commit)
├── .env.example       # Template for .env
├── config.py          # Settings loader (pydantic)
├── main.py            # Entry point
├── requirements.txt   # Pinned deps
└── CLAUDE.md          # This file
```

## Asosiy funksiyalar (Roadmap)

### MVP (1-bosqich)
- [x] Loyiha skeleti
- [ ] `/start` — til tanlash, menyu
- [ ] **Anonim murojaat** — shikoyat yuborish (foto/video/audio bilan)
- [ ] Murojaat raqami (tracking ID) — keyin holatni tekshirish
- [ ] Adminlarga bildirish
- [ ] FAQ — huquqlar haqida
- [ ] Ishonch telefoni va kontakt ma'lumotlari

### 2-bosqich
- [ ] Psixolog bilan anonim chat
- [ ] Hodisa turlari bo'yicha klassifikatsiya
- [ ] Statistika dashboard (admin)
- [ ] PDF hisobot generatsiya
- [ ] Geolokatsiya (kampusda joy)

### 3-bosqich
- [ ] Web admin panel (FastAPI)
- [ ] Multi-bilingual (uz/ru/en)
- [ ] Push notification adminlarga
- [ ] Buyruq matnlari va huquqiy materiallar bazasi

## Foydalanuvchi rollari

1. **Talaba/Xodim** — anonim murojaat yuboradi, holatini kuzatadi
2. **Psixolog** — talabaga maslahat beradi
3. **Huquqiy yordam xodimi** — yuridik masalalar
4. **Komissiya a'zosi** — murojaatlarni ko'rib chiqadi
5. **Super admin** — to'liq nazorat, statistika, sozlamalar

## Xavfsizlik talablari

- **Anonimlik birinchi o'rinda** — foydalanuvchi ID hash qilib saqlanadi
- Maxfiy ma'lumotlar shifrlangan holda saqlanadi (cryptography.fernet)
- Adminlarga yuborilgan murojaatlar audit log'ga yoziladi
- Rate limiting (anti-spam): 1 murojaat / 5 daqiqa
- Ma'lumotlar O'zbekiston serverlarida joylashtirilishi kerak (keyinchalik)

## Komandalar (kelajakda)

```bash
# Botni ishga tushirish
python main.py

# Test
pytest

# DB migratsiya
python scripts/migrate.py

# Backup
python scripts/backup.py
```

## Working notes for Claude

- **Til:** Foydalanuvchi o'zbek tilida yozadi. Javoblar o'zbek tilida bo'lsin (qisqacha, aniq).
- **Kod:** Type hints, docstrings minimal — faqat zarur joyda. async/await dan foydalan.
- **aiogram 3:** Router-based architecture. Magic filters. FSM context.
- **DB:** Migration'larni `scripts/` ga yoz. Schema o'zgarsa, CLAUDE.md ni yangilash.
- **Secrets:** Hech qachon .env'ni commit qilma. .env.example faqat shablon.
- **Test:** Yangi handler yozilsa, test ham yozilsin (tests/).
- **Log:** Loguru. INFO darajada production, DEBUG dev rejimida.
