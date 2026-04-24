"""
Middlewares:
- LanguageMiddleware:  ensures user exists in DB, injects `lang` into handler data.
- BlockedUserMiddleware: stops blocked users with a single reply.
"""
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from bot import services
from bot.utils.i18n import t

logger = logging.getLogger(__name__)


class LanguageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user = None
        if isinstance(event, (Message, CallbackQuery)):
            tg_user = event.from_user

        lang = 'en'
        db_user = None
        if tg_user:
            try:
                db_user = await services.get_or_create_user(
                    telegram_id=tg_user.id,
                    username=tg_user.username,
                    first_name=tg_user.first_name or '',
                    last_name=tg_user.last_name or '',
                )
                if db_user and db_user.language:
                    lang = db_user.language.code
            except Exception as e:
                logger.error(f'LanguageMiddleware: {e}')

        data['lang'] = lang
        data['db_user'] = db_user
        return await handler(event, data)


class BlockedUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        db_user = data.get('db_user')
        lang = data.get('lang', 'en')
        if db_user and db_user.is_blocked:
            msg = t(lang, 'blocked')
            try:
                if isinstance(event, Message):
                    await event.answer(msg)
                elif isinstance(event, CallbackQuery):
                    await event.answer(msg, show_alert=True)
            except Exception:
                pass
            return  # stop the chain
        return await handler(event, data)
