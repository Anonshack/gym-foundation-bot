"""
Signals for payments:
- When a new Payment is created with status='pending', notify the admin group.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Payment)
def notify_admin_on_new_payment(sender, instance, created, **kwargs):
    """When a new pending payment is created, send screenshot to admin group."""
    if not created:
        return
    if instance.status != 'pending':
        return
    try:
        # Import inside signal to avoid circular imports
        from bot.utils.notifier import notify_admin_new_payment
        notify_admin_new_payment(instance)
    except Exception as e:
        logger.exception(f'Failed to notify admin about new payment #{instance.id}: {e}')
