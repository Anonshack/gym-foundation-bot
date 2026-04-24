"""
All Django ORM access for the bot (async-safe via sync_to_async).
"""
import logging
from asgiref.sync import sync_to_async
from django.utils import timezone

logger = logging.getLogger(__name__)


# ─── USERS ───────────────────────────────────────────────────────────────────

@sync_to_async
def get_or_create_user(telegram_id: int, username: str = None, first_name: str = '', last_name: str = ''):
    from apps.users.models import TelegramUser
    user, created = TelegramUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={'username': username or '', 'first_name': first_name or '', 'last_name': last_name or ''},
    )
    if not created:
        # Keep username/name fresh
        changed = False
        if username and user.username != username:
            user.username = username; changed = True
        if first_name and user.first_name != first_name:
            user.first_name = first_name; changed = True
        if last_name is not None and user.last_name != last_name:
            user.last_name = last_name; changed = True
        if changed:
            user.save(update_fields=['username', 'first_name', 'last_name', 'updated_at'])
    return user


@sync_to_async
def get_user(telegram_id: int):
    from apps.users.models import TelegramUser
    try:
        return TelegramUser.objects.select_related('language').get(telegram_id=telegram_id)
    except TelegramUser.DoesNotExist:
        return None


@sync_to_async
def set_user_language(telegram_id: int, lang_code: str) -> bool:
    from apps.users.models import TelegramUser, Language
    try:
        lang, _ = Language.objects.get_or_create(
            code=lang_code,
            defaults={'name': {'uz': "O'zbek", 'ru': 'Русский', 'en': 'English'}.get(lang_code, lang_code)},
        )
        TelegramUser.objects.filter(telegram_id=telegram_id).update(language=lang)
        return True
    except Exception as e:
        logger.error(f'set_user_language: {e}')
        return False


@sync_to_async
def get_user_language(telegram_id: int) -> str:
    from apps.users.models import TelegramUser
    try:
        u = TelegramUser.objects.select_related('language').get(telegram_id=telegram_id)
        return u.language.code if u.language else 'en'
    except TelegramUser.DoesNotExist:
        return 'en'


@sync_to_async
def set_user_subscribed(telegram_id: int, subscribed: bool = True):
    from apps.users.models import TelegramUser
    TelegramUser.objects.filter(telegram_id=telegram_id).update(is_subscribed=subscribed)


@sync_to_async
def is_user_blocked(telegram_id: int) -> bool:
    from apps.users.models import TelegramUser
    return TelegramUser.objects.filter(telegram_id=telegram_id, is_blocked=True).exists()


# ─── PROGRAMS / MEMBERSHIP / TRAINERS ────────────────────────────────────────

@sync_to_async
def list_programs():
    from apps.gym.models import GymProgram
    return list(GymProgram.objects.filter(is_active=True).select_related('trainer').order_by('name'))


@sync_to_async
def get_program(program_id: int):
    from apps.gym.models import GymProgram
    try:
        return GymProgram.objects.select_related('trainer').get(id=program_id, is_active=True)
    except GymProgram.DoesNotExist:
        return None


@sync_to_async
def list_membership_plans():
    from apps.gym.models import MembershipPlan
    return list(MembershipPlan.objects.filter(is_active=True).order_by('price_monthly_uzs'))


@sync_to_async
def list_trainers():
    from apps.users.models import Trainer
    return list(Trainer.objects.filter(is_active=True).order_by('name'))


@sync_to_async
def list_nutrition_plans():
    from apps.gym.models import NutritionPlan
    return list(NutritionPlan.objects.filter(is_active=True).select_related('program').order_by('name'))


@sync_to_async
def list_discounts():
    from apps.gym.models import Discount
    now = timezone.now()
    return list(Discount.objects.filter(is_active=True, valid_from__lte=now, valid_until__gte=now).order_by('-discount_percent'))


@sync_to_async
def list_testimonials():
    from apps.gym.models import Testimonial
    return list(Testimonial.objects.filter(is_approved=True).select_related('user', 'program').order_by('-created_at')[:10])


@sync_to_async
def list_schedules():
    from apps.gym.models import Schedule
    return list(Schedule.objects.select_related('program', 'trainer').order_by('day_of_week', 'start_time'))


# ─── PAYMENT CARDS ───────────────────────────────────────────────────────────

@sync_to_async
def list_payment_cards():
    from apps.payments.models import PaymentCard
    return list(PaymentCard.objects.filter(is_active=True).order_by('bank_name'))


# ─── ENROLLMENT + PAYMENT ────────────────────────────────────────────────────

@sync_to_async
def create_payment_with_screenshot(telegram_id: int, program_id: int, file_bytes: bytes, filename: str = 'screenshot.jpg'):
    """Create Enrollment + Payment, save the downloaded screenshot bytes to MEDIA."""
    from django.core.files.base import ContentFile
    from apps.users.models import TelegramUser
    from apps.gym.models import GymProgram
    from apps.enrollments.models import Enrollment
    from apps.payments.models import Payment, PaymentHistory

    user = TelegramUser.objects.get(telegram_id=telegram_id)
    program = GymProgram.objects.get(id=program_id)

    enrollment, _ = Enrollment.objects.get_or_create(
        user=user, program=program,
        defaults={'status': 'pending'},
    )
    if enrollment.status in ('cancelled', 'completed'):
        enrollment.status = 'pending'
        enrollment.save(update_fields=['status', 'updated_at'])

    payment = Payment(
        user=user,
        enrollment=enrollment,
        program=program,
        payment_type='program',
        amount_uzs=program.price_uzs,
        amount_usd=program.price_usd,
        currency='UZS',
        status='pending',
    )
    payment.screenshot.save(filename, ContentFile(file_bytes), save=False)
    payment.save()

    PaymentHistory.objects.create(
        payment=payment, status='screenshot_uploaded',
        comment='Screenshot uploaded by user via Telegram bot',
    )
    return payment
