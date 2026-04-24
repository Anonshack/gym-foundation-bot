"""
Admin-group handlers for the Approve / Reject buttons on new payment notifications.
Only users whose chat id is ADMIN_GROUP_ID or whose id is in ADMIN_TELEGRAM_IDS can act.
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)
router = Router(name='admin_actions')


def _is_authorized(user_id: int, chat_id: int) -> bool:
    admin_chat = str(settings.ADMIN_GROUP_ID or '0')
    admin_ids = {str(x).strip() for x in settings.ADMIN_TELEGRAM_IDS if str(x).strip()}
    return str(chat_id) == admin_chat or str(user_id) in admin_ids


@router.callback_query(F.data.startswith('adm_app:'))
async def cb_admin_approve(callback: CallbackQuery):
    if not _is_authorized(callback.from_user.id, callback.message.chat.id):
        await callback.answer('⛔ Not authorized', show_alert=True)
        return
    try:
        payment_id = int(callback.data.split(':', 1)[1])
    except ValueError:
        await callback.answer()
        return

    ok, msg = await _do_approve(payment_id, callback.from_user.id)
    await callback.answer(msg, show_alert=True)
    if ok:
        await _update_admin_message(callback, f'✅ APPROVED by @{callback.from_user.username or callback.from_user.id}')


@router.callback_query(F.data.startswith('adm_rej:'))
async def cb_admin_reject(callback: CallbackQuery):
    if not _is_authorized(callback.from_user.id, callback.message.chat.id):
        await callback.answer('⛔ Not authorized', show_alert=True)
        return
    try:
        payment_id = int(callback.data.split(':', 1)[1])
    except ValueError:
        await callback.answer()
        return

    ok, msg = await _do_reject(payment_id, callback.from_user.id)
    await callback.answer(msg, show_alert=True)
    if ok:
        await _update_admin_message(callback, f'❌ REJECTED by @{callback.from_user.username or callback.from_user.id}')


async def _update_admin_message(callback: CallbackQuery, status_line: str):
    """Strip the inline buttons and append the decision line to the caption/text."""
    try:
        if callback.message.caption is not None:
            new_caption = callback.message.caption + f'\n\n<b>{status_line}</b>'
            await callback.message.edit_caption(caption=new_caption, reply_markup=None)
        else:
            new_text = (callback.message.text or '') + f'\n\n<b>{status_line}</b>'
            await callback.message.edit_text(new_text, reply_markup=None)
    except Exception as e:
        logger.warning(f'Could not edit admin message: {e}')


# ─── ORM operations (sync → async) ───────────────────────────────────────────

@sync_to_async
def _approve_payment(payment_id: int, admin_telegram_id: int):
    from apps.payments.models import Payment, PaymentHistory
    payment = Payment.objects.select_related('user', 'program', 'enrollment').get(id=payment_id)
    if payment.status != 'pending':
        return False, f'Already {payment.status}', payment

    payment.status = 'approved'
    payment.approved_at = timezone.now()
    payment.save(update_fields=['status', 'approved_at', 'updated_at'])

    if payment.enrollment:
        payment.enrollment.status = 'active'
        payment.enrollment.save(update_fields=['status', 'updated_at'])

    PaymentHistory.objects.create(
        payment=payment, status='approved',
        comment=f'Approved by admin TG id {admin_telegram_id}',
    )
    return True, 'Approved ✅', payment


@sync_to_async
def _reject_payment(payment_id: int, admin_telegram_id: int):
    from apps.payments.models import Payment, PaymentHistory
    payment = Payment.objects.select_related('user', 'program', 'enrollment').get(id=payment_id)
    if payment.status != 'pending':
        return False, f'Already {payment.status}', payment

    payment.status = 'rejected'
    payment.rejected_at = timezone.now()
    payment.rejection_reason = f'Rejected by admin {admin_telegram_id}'
    payment.save(update_fields=['status', 'rejected_at', 'rejection_reason', 'updated_at'])

    if payment.enrollment:
        payment.enrollment.status = 'cancelled'
        payment.enrollment.save(update_fields=['status', 'updated_at'])

    PaymentHistory.objects.create(
        payment=payment, status='rejected',
        comment=f'Rejected by admin TG id {admin_telegram_id}',
    )
    return True, 'Rejected ❌', payment


async def _do_approve(payment_id: int, admin_id: int):
    try:
        ok, msg, payment = await _approve_payment(payment_id, admin_id)
        if ok:
            # Notify user via HTTP API (sync helper runs inside sync_to_async)
            await _notify_user_approved(payment)
        return ok, msg
    except Exception as e:
        logger.exception('approve failed')
        return False, f'Error: {e}'


async def _do_reject(payment_id: int, admin_id: int):
    try:
        ok, msg, payment = await _reject_payment(payment_id, admin_id)
        if ok:
            await _notify_user_rejected(payment)
        return ok, msg
    except Exception as e:
        logger.exception('reject failed')
        return False, f'Error: {e}'


@sync_to_async
def _notify_user_approved(payment):
    from bot.utils.notifier import notify_user_payment_approved
    notify_user_payment_approved(payment)


@sync_to_async
def _notify_user_rejected(payment):
    from bot.utils.notifier import notify_user_payment_rejected
    notify_user_payment_rejected(payment)
