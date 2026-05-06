# Himoya Bot — TashMedUni

Toshkent tibbiyot universiteti uchun anonim murojaat va himoya tizimi Telegram boti.

**Bot:** [@himoya_tashmedunitf_bot](https://t.me/himoya_tashmedunitf_bot)

## Asos

Oliy ta'lim, fan va innovatsiyalar vazirligining 2026-yil 20-apreldagi **150-sonli buyrug'i** — "Ta'lim muassasasida o'quvchi-talaba qizlarning huquq va xavfsizligini ta'minlash hamda shilqimlik (harassment), tazyiq holatlarining oldini olish to'g'risida".

## Funksiyalar

- 🔒 Anonim murojaat (foto/video/audio bilan)
- 📋 Murojaat holatini kuzatish (tracking ID)
- 👨‍⚖️ Huquqiy yordam ma'lumotlari
- 🧠 Psixologik ko'mak
- 📞 Ishonch telefoni
- 📖 Huquqlar haqida FAQ

## O'rnatish

```bash
# 1. Repo'ni klonlash
git clone <repo-url>
cd himoya_tashmedunitf_bot

# 2. Virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Dependencies
pip install -r requirements.txt

# 4. .env ni sozlash
copy .env.example .env
# .env'ni tahrirlab BOT_TOKEN va ADMIN_IDS qo'ying

# 5. Ishga tushirish
python main.py
```

## Texnologiyalar

- Python 3.14+
- aiogram 3.x
- SQLAlchemy 2 (async) + SQLite/PostgreSQL
- pydantic-settings
- loguru

## Litsenziya

Toshkent tibbiyot universiteti ichki loyihasi.
