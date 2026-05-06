"""Bot komandalarini Telegram'da ro'yxatdan o'tkazish."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from aiogram import Bot  # noqa: E402
from aiogram.types import (  # noqa: E402
    BotCommand,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeAllChatAdministrators,
)

from config import settings  # noqa: E402


COMMANDS_UZ = [
    BotCommand(command="start", description="🚀 Botni ishga tushirish / Asosiy menyu"),
    BotCommand(command="profile", description="👤 Mening profilim"),
    BotCommand(command="my_reports", description="📋 Mening murojaatlarim"),
    BotCommand(command="language", description="🌐 Tilni o'zgartirish"),
    BotCommand(command="cancel", description="❌ Joriy amalni bekor qilish"),
    BotCommand(command="help", description="ℹ️ Yordam"),
]

COMMANDS_ADMIN = COMMANDS_UZ + [
    BotCommand(command="admin", description="👮 Admin panel"),
]


async def main() -> None:
    bot = Bot(token=settings.bot_token)
    try:
        # Webhook'ni o'chiramiz (polling rejimida ishlaymiz)
        await bot.delete_webhook(drop_pending_updates=True)
        print("[OK] Webhook o'chirildi (drop_pending_updates=True)")

        # Default scope (hamma joyda)
        await bot.set_my_commands(COMMANDS_UZ)
        # Private chats uchun ham
        await bot.set_my_commands(
            COMMANDS_UZ,
            scope=BotCommandScopeAllPrivateChats(),
        )
        print(f"[OK] {len(COMMANDS_UZ)} ta komanda ro'yxatdan o'tkazildi (default + private)")

        # Adminlar uchun
        if settings.admin_ids:
            from aiogram.types import BotCommandScopeChat

            for admin_id in settings.admin_ids:
                await bot.set_my_commands(
                    COMMANDS_ADMIN,
                    scope=BotCommandScopeChat(chat_id=admin_id),
                )
            print(f"[OK] {len(COMMANDS_ADMIN)} ta admin komandasi {len(settings.admin_ids)} ta admin uchun")

        # Bot info
        me = await bot.get_me()
        print(f"\n[OK] Bot: @{me.username}")
        print(f"     ID: {me.id}")
        print(f"     Description: {me.first_name}")

        # Joriy commands
        cmds = await bot.get_my_commands()
        print(f"\n[OK] Hozirgi komandalar ({len(cmds)}):")
        for c in cmds:
            print(f"     /{c.command} — {c.description}")

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
