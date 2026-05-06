"""Bot entry point."""
from __future__ import annotations

import asyncio
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from bot.database.db import close_db, init_db
from bot.handlers import router as root_router
from bot.middlewares.db import DbSessionMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware
from bot.utils.logger import setup_logger
from config import settings


async def on_startup(bot: Bot) -> None:
    await init_db()
    me = await bot.get_me()
    logger.info(f"Bot ishga tushdi: @{me.username} (id={me.id})")
    if settings.admin_ids:
        logger.info(f"Adminlar: {settings.admin_ids}")


async def on_shutdown(bot: Bot) -> None:
    logger.info("Bot to'xtatilmoqda...")
    await close_db()
    await bot.session.close()


async def main() -> None:
    setup_logger()

    if settings.redis_url:
        from aiogram.fsm.storage.redis import RedisStorage

        storage = RedisStorage.from_url(settings.redis_url)
        logger.info("FSM storage: Redis")
    else:
        storage = MemoryStorage()
        logger.info("FSM storage: Memory")

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)

    dp.update.middleware(DbSessionMiddleware())
    dp.message.middleware(ThrottlingMiddleware(rate=0.1))

    dp.include_router(root_router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi (Ctrl+C)")
