"""Telegram bot — main entry point.

Usage:
    python -m src.bot.main
"""

import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import structlog

from src.core.config import settings
from src.core.logging import setup_logging
from src.bot.handlers import router

logger = structlog.get_logger()


async def main() -> None:
    setup_logging()

    if not settings.bot_token:
        logger.error("BOT_TOKEN is not set in .env")
        sys.exit(1)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # TODO: replace MemoryStorage with RedisStorage in Phase 2
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)

    logger.info("bot_starting", username=(await bot.me()).username)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
