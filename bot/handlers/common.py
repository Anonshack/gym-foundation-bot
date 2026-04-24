"""
Common flow: /start → language → subscription check → main menu.
Also handles `menu:home` callback to return to the main menu.
"""
import logging
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from django.conf import settings

from bot import services
from bot.keyboards import (
    language_keyboard, subscription_keyboard, main_menu_keyboard,
)
from bot.states import UserFlow
from bot.utils.i18n import t

logger = logging.getLogger(__name__)
router = Router(name='common')


# ─── /start ──────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, lang: str, db_user):
    await state.clear()
    await message.answer(
        t(lang, 'welcome'),
        reply_markup=language_keyboard(),
    )
    await state.set_state(UserFlow.choosing_language)


# ─── Language choice ─────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith('lang:'))
async def cb_language(callback: CallbackQuery, state: FSMContext):
    lang_code = callback.data.split(':', 1)[1]
    if lang_code not in ('uz', 'ru', 'en'):
        await callback.answer()
        return

    await services.set_user_language(callback.from_user.id, lang_code)
    await callback.answer(t(lang_code, 'language_selected'))

    channel_url = _channel_url()
    await _edit_or_send(
        callback,
        text=t(lang_code, 'subscribe_title'),
        reply_markup=subscription_keyboard(lang_code, channel_url),
    )
    await state.set_state(UserFlow.checking_subscription)


# ─── Subscription check ──────────────────────────────────────────────────────

@router.callback_query(F.data == 'sub:check')
async def cb_check_subscription(callback: CallbackQuery, state: FSMContext, lang: str):
    is_subscribed = await _check_channel_membership(callback.bot, callback.from_user.id)

    if is_subscribed:
        await services.set_user_subscribed(callback.from_user.id, True)
        await callback.answer(t(lang, 'subscribed_ok'))
        await _edit_or_send(
            callback,
            text=t(lang, 'main_menu'),
            reply_markup=main_menu_keyboard(lang),
        )
        await state.set_state(UserFlow.in_main_menu)
    else:
        await callback.answer(t(lang, 'not_subscribed'), show_alert=True)


# ─── Home (come back to main menu) ───────────────────────────────────────────

@router.callback_query(F.data == 'menu:home')
async def cb_menu_home(callback: CallbackQuery, state: FSMContext, lang: str):
    await state.set_state(UserFlow.in_main_menu)
    await _edit_or_send(
        callback,
        text=t(lang, 'main_menu'),
        reply_markup=main_menu_keyboard(lang),
    )
    await callback.answer()


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _channel_url() -> str:
    """Build the public t.me URL for the configured channel."""
    ch = settings.CHANNEL_ID or ''
    username = settings.CHANNEL_USERNAME or ''
    if username:
        username = username.lstrip('@')
        return f'https://t.me/{username}'
    if isinstance(ch, str) and ch.startswith('@'):
        return f'https://t.me/{ch[1:]}'
    return 'https://t.me/'


async def _check_channel_membership(bot: Bot, user_id: int) -> bool:
    """
    Check whether the user is a member of the configured channel.
    Returns True when subscribed, False otherwise (including when the bot
    can't verify — in that case we assume False, user can press again).
    If CHANNEL_ID is not set at all, we pass through (True) for dev convenience.
    """
    ch = settings.CHANNEL_ID
    if not ch:
        logger.warning('CHANNEL_ID not set — skipping subscription check')
        return True

    # Normalize channel id (accept @username or -100... numeric)
    chat_id = ch.strip()
    if chat_id.lstrip('-').isdigit():
        chat_id = int(chat_id)

    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ('member', 'administrator', 'creator', 'restricted')
    except TelegramBadRequest as e:
        logger.warning(f'Subscription check failed ({e}). Make sure the bot is admin in the channel.')
        return False
    except Exception as e:
        logger.error(f'Subscription check error: {e}')
        return False


async def _edit_or_send(callback: CallbackQuery, text: str, reply_markup=None):
    """Edit the message if possible; otherwise send a new one (photos can't be edit_text-ed)."""
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass
        await callback.message.answer(text, reply_markup=reply_markup)
