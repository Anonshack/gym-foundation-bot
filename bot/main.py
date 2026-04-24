"""
Bot entry point.
Run:   python -m bot.main
"""
import asyncio
import logging
import os
import sys
from pathlib import Path

# ─── Django bootstrap (must happen before any apps import) ───────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django  # noqa: E402
django.setup()

# ─── Now safe to import Django & bot modules ─────────────────────────────────
from aiogram import Bot, Dispatcher  # noqa: E402
from aiogram.client.default import DefaultBotProperties  # noqa: E402
from aiogram.enums import ParseMode  # noqa: E402
from aiogram.fsm.storage.memory import MemoryStorage  # noqa: E402
from django.conf import settings  # noqa: E402

from bot.middlewares import LanguageMiddleware, BlockedUserMiddleware  # noqa: E402
from bot.handlers import admin as h_admin, common, enrollment, info, ai  # noqa: E402

logger = logging.getLogger('bot')


async def main():
    token = (settings.BOT_TOKEN or '').strip()
    if not token:
        logger.error('❌ BOT_TOKEN is not set. Add it to .env and restart.')
        sys.exit(1)

    # Storage: Redis if REDIS_URL set, otherwise in-memory
    storage = MemoryStorage()
    if settings.REDIS_URL:
        try:
            from aiogram.fsm.storage.redis import RedisStorage
            storage = RedisStorage.from_url(settings.REDIS_URL)
            logger.info('📦 Using Redis FSM storage')
        except Exception as e:
            logger.warning(f'Redis not available ({e}), falling back to MemoryStorage')

    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)

    # ─── Middlewares (applied to messages & callbacks) ───────────────────────
    dp.message.middleware(LanguageMiddleware())
    dp.callback_query.middleware(LanguageMiddleware())
    dp.message.middleware(BlockedUserMiddleware())
    dp.callback_query.middleware(BlockedUserMiddleware())

    # ─── Routers (order matters: admin first so group callbacks intercept) ───
    dp.include_router(h_admin.router)     # admin-group approve/reject
    dp.include_router(common.router)      # /start, language, subscription, menu home
    dp.include_router(enrollment.router)  # program selection + screenshot
    dp.include_router(ai.router)          # AI assistant
    dp.include_router(info.router)        # about, contact, membership, results, etc.

    # ─── Launch polling ──────────────────────────────────────────────────────
    me = await bot.get_me()
    logger.info(f'🤖 Bot @{me.username} is up. Polling…')

    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info('Bot stopped.')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('\n🛑 Bot stopped')
