"""
Synchronous Telegram notifier.
Uses Telegram Bot API over plain HTTPS (via `requests`), so it works from:
  - Django signals
  - Admin actions / views
  - Management commands
…without needing an asyncio event loop.
"""
import logging
from pathlib import Path
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

TELEGRAM_API = 'https://api.telegram.org/bot{token}/{method}'


def _api_call(method: str, data: dict = None, files: dict = None, timeout: int = 10):
    """Low-level Telegram Bot API call."""
    token = settings.BOT_TOKEN
    if not token:
        logger.warning('BOT_TOKEN not set — skipping Telegram notification')
        return None
    url = TELEGRAM_API.format(token=token, method=method)
    try:
        resp = requests.post(url, data=data, files=files, timeout=timeout)
        if resp.status_code != 200:
            logger.error(f'Telegram API error {resp.status_code}: {resp.text}')
            return None
        return resp.json()
    except requests.RequestException as e:
        logger.error(f'Telegram request failed: {e}')
        return None


def send_message(chat_id, text: str, parse_mode: str = 'HTML', reply_markup: dict = None):
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}
    if reply_markup:
        import json
        data['reply_markup'] = json.dumps(reply_markup)
    return _api_call('sendMessage', data=data)


def send_photo(chat_id, photo_path: str, caption: str = '', parse_mode: str = 'HTML', reply_markup: dict = None):
    data = {'chat_id': chat_id, 'caption': caption, 'parse_mode': parse_mode}
    if reply_markup:
        import json
        data['reply_markup'] = json.dumps(reply_markup)
    try:
        with open(photo_path, 'rb') as f:
            files = {'photo': f}
            return _api_call('sendPhoto', data=data, files=files, timeout=30)
    except FileNotFoundError:
        logger.error(f'Photo not found: {photo_path}')
        return None


# ─── High-level helpers for Payment flow ─────────────────────────────────────

PROGRAM_EMOJI = {
    'weight_loss': '⚖️', 'muscle_gain': '💪', 'boxing': '🥊',
    'crossfit': '🏋️', 'personal_training': '👨‍🏫',
    'women_fitness': '👩‍🦰', 'teen_fitness': '🧒',
}


def notify_admin_new_payment(payment):
    """Send screenshot + info to admin group. Called from post_save signal."""
    group_id = settings.ADMIN_GROUP_ID
    if not group_id or str(group_id) in ('0', ''):
        logger.warning('ADMIN_GROUP_ID not set — cannot notify admins of new payment')
        return

    user = payment.user
    program = payment.program or (payment.enrollment.program if payment.enrollment else None)
    program_name = program.name if program else '—'
    program_emoji = PROGRAM_EMOJI.get(program.code, '🏋️') if program else '💰'

    username = f'@{user.username}' if user.username else '—'

    caption = (
        f'🔔 <b>NEW PAYMENT</b> #{payment.id}\n'
        f'━━━━━━━━━━━━━━━━━━━━━\n'
        f'👤 <b>User:</b> {user.full_name}\n'
        f'🆔 <b>Telegram:</b> <code>{user.telegram_id}</code>\n'
        f'📱 <b>Username:</b> {username}\n\n'
        f'{program_emoji} <b>Program:</b> {program_name}\n'
        f'💰 <b>Amount:</b> {int(payment.amount_uzs):,} so‘m / ${payment.amount_usd:.2f}\n'
        f'🕐 <b>Time:</b> {payment.created_at.strftime("%Y-%m-%d %H:%M")}\n'
        f'━━━━━━━━━━━━━━━━━━━━━\n'
        f'Review in admin panel and approve or reject below.'
    )

    # Inline keyboard: Approve / Reject via /approve_ID and /reject_ID
    reply_markup = {
        'inline_keyboard': [[
            {'text': '✅ Approve', 'callback_data': f'admin_approve_{payment.id}'},
            {'text': '❌ Reject',  'callback_data': f'admin_reject_{payment.id}'},
        ]]
    }

    if payment.screenshot and Path(payment.screenshot.path).exists():
        send_photo(group_id, payment.screenshot.path, caption=caption, reply_markup=reply_markup)
    else:
        send_message(group_id, caption, reply_markup=reply_markup)


def notify_user_payment_approved(payment):
    """Tell the user their payment was approved. Multilingual."""
    user = payment.user
    lang = user.language.code if user.language else 'en'
    program = payment.program or (payment.enrollment.program if payment.enrollment else None)
    program_name = program.name if program else ''

    texts = {
        'uz': (
            f'🎉 <b>TABRIKLAYMIZ!</b>\n'
            f'━━━━━━━━━━━━━━━━━━━━━\n'
            f'✅ To‘lovingiz tasdiqlandi!\n\n'
            f'🏋️ <b>Dastur:</b> {program_name}\n\n'
            f'Tez orada trenerimiz siz bilan bog‘lanadi.\n'
            f'Yangi boshlanish uchun tayyor bo‘ling! 💪'
        ),
        'ru': (
            f'🎉 <b>ПОЗДРАВЛЯЕМ!</b>\n'
            f'━━━━━━━━━━━━━━━━━━━━━\n'
            f'✅ Ваш платёж подтверждён!\n\n'
            f'🏋️ <b>Программа:</b> {program_name}\n\n'
            f'Тренер скоро свяжется с вами.\n'
            f'Готовьтесь к новому старту! 💪'
        ),
        'en': (
            f'🎉 <b>CONGRATULATIONS!</b>\n'
            f'━━━━━━━━━━━━━━━━━━━━━\n'
            f'✅ Your payment is approved!\n\n'
            f'🏋️ <b>Program:</b> {program_name}\n\n'
            f'Your trainer will contact you soon.\n'
            f'Get ready for a new start! 💪'
        ),
    }
    send_message(user.telegram_id, texts.get(lang, texts['en']))


def notify_user_payment_rejected(payment, reason: str = ''):
    user = payment.user
    lang = user.language.code if user.language else 'en'
    program = payment.program or (payment.enrollment.program if payment.enrollment else None)
    program_name = program.name if program else ''
    reason_line_uz = f'\n💬 <b>Sabab:</b> {reason}' if reason else ''
    reason_line_ru = f'\n💬 <b>Причина:</b> {reason}' if reason else ''
    reason_line_en = f'\n💬 <b>Reason:</b> {reason}' if reason else ''

    texts = {
        'uz': (
            f'❌ <b>AFSUSKI</b>\n'
            f'━━━━━━━━━━━━━━━━━━━━━\n'
            f'To‘lovingiz rad etildi.\n\n'
            f'🏋️ <b>Dastur:</b> {program_name}{reason_line_uz}\n\n'
            f'Qayta to‘lov qiling yoki admin bilan bog‘laning.'
        ),
        'ru': (
            f'❌ <b>К СОЖАЛЕНИЮ</b>\n'
            f'━━━━━━━━━━━━━━━━━━━━━\n'
            f'Ваш платёж отклонён.\n\n'
            f'🏋️ <b>Программа:</b> {program_name}{reason_line_ru}\n\n'
            f'Повторите оплату или свяжитесь с администратором.'
        ),
        'en': (
            f'❌ <b>WE ARE SORRY</b>\n'
            f'━━━━━━━━━━━━━━━━━━━━━\n'
            f'Your payment was rejected.\n\n'
            f'🏋️ <b>Program:</b> {program_name}{reason_line_en}\n\n'
            f'Please try again or contact our admin.'
        ),
    }
    send_message(user.telegram_id, texts.get(lang, texts['en']))
