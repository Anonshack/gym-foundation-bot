"""
`python manage.py seed_demo` — populate the database with sample content
so the bot has something to show immediately.

Idempotent: safe to run multiple times.
"""
from datetime import datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Seed the database with demo content (languages, programs, plans, cards, trainers).'

    def handle(self, *args, **options):
        from apps.users.models import Language, Trainer
        from apps.gym.models import GymProgram, MembershipPlan, Schedule, NutritionPlan, Discount
        from apps.payments.models import PaymentCard, PaymentMethod, PaymentSettings

        created = 0
        updated = 0

        # ── Languages ────────────────────────────────────────────────
        for code, name in [('uz', "O'zbek"), ('ru', 'Русский'), ('en', 'English')]:
            _, was_created = Language.objects.update_or_create(
                code=code, defaults={'name': name},
            )
            created += int(was_created); updated += int(not was_created)

        # ── Trainers ─────────────────────────────────────────────────
        trainers_data = [
            {
                'name': 'Alisher Karimov', 'specialization': 'Muscle Gain & Strength',
                'bio': 'Certified personal trainer with 8 years of experience. Specializes in hypertrophy and powerlifting.',
                'phone': '+998 90 123 45 67', 'telegram_username': 'alisher_coach',
                'experience_years': 8, 'is_active': True,
            },
            {
                'name': 'Malika Yusupova', 'specialization': 'Women Fitness & Yoga',
                'bio': 'Yoga & women-focused fitness expert. Helping clients feel great for 6+ years.',
                'phone': '+998 91 234 56 78', 'telegram_username': 'malika_fit',
                'experience_years': 6, 'is_active': True,
            },
            {
                'name': 'Bekzod Rahimov', 'specialization': 'Boxing & Martial Arts',
                'bio': 'Former national boxing champion. Master of combat sports training.',
                'phone': '+998 93 345 67 89', 'telegram_username': 'bek_boxing',
                'experience_years': 12, 'is_active': True,
            },
        ]
        for t in trainers_data:
            _, was_created = Trainer.objects.update_or_create(
                name=t['name'], defaults=t,
            )
            created += int(was_created); updated += int(not was_created)

        alisher = Trainer.objects.filter(name='Alisher Karimov').first()
        malika = Trainer.objects.filter(name='Malika Yusupova').first()
        bekzod = Trainer.objects.filter(name='Bekzod Rahimov').first()

        # ── Gym Programs ─────────────────────────────────────────────
        programs_data = [
            {
                'code': 'weight_loss', 'name': 'Weight Loss Pro',
                'description': 'A comprehensive 30-day program designed for healthy, sustainable fat loss.',
                'price_uzs': Decimal('800000'), 'price_usd': Decimal('65.00'),
                'duration_days': 30, 'trainer': malika,
                'benefits': "Personal coach support\nCustom meal plan\nProgress tracking\nCardio + strength mix\nFlexible schedule",
                'requirements': "Doctor's clearance\nMinimum age 16\nCommitment: 4 sessions/week",
            },
            {
                'code': 'muscle_gain', 'name': 'Muscle Gain Elite',
                'description': 'Build serious muscle mass with progressive overload training.',
                'price_uzs': Decimal('1000000'), 'price_usd': Decimal('80.00'),
                'duration_days': 60, 'trainer': alisher,
                'benefits': "Hypertrophy-focused programming\nHigh-protein meal plan\nSupplement guide\nVideo form checks\nRecovery protocols",
                'requirements': "Minimum 6 months training experience\nBasic medical check\nReady for 5 sessions/week",
            },
            {
                'code': 'boxing', 'name': 'Boxing Champion',
                'description': 'Master boxing technique with former national champion.',
                'price_uzs': Decimal('1200000'), 'price_usd': Decimal('95.00'),
                'duration_days': 45, 'trainer': bekzod,
                'benefits': "Technical training\nSparring practice\nConditioning workouts\nMental preparation\nEquipment included",
                'requirements': "Age 16+\nPhysical fitness baseline\nProtective gear (provided)",
            },
            {
                'code': 'crossfit', 'name': 'CrossFit Intensity',
                'description': 'High-intensity functional training for all-around fitness.',
                'price_uzs': Decimal('900000'), 'price_usd': Decimal('72.00'),
                'duration_days': 30, 'trainer': alisher,
                'benefits': "Varied daily workouts\nStrength + cardio\nCommunity environment\nNutrition coaching",
                'requirements': "Basic fitness level\nCompetitive mindset",
            },
            {
                'code': 'women_fitness', 'name': 'Women Fitness Club',
                'description': 'Female-only group classes tailored for women of all levels.',
                'price_uzs': Decimal('600000'), 'price_usd': Decimal('48.00'),
                'duration_days': 30, 'trainer': malika,
                'benefits': "Women-only environment\nYoga + pilates mix\nNutrition tips\nMental wellness sessions",
                'requirements': "No experience required",
            },
        ]
        for p in programs_data:
            _, was_created = GymProgram.objects.update_or_create(
                code=p['code'], defaults={**p, 'is_active': True},
            )
            created += int(was_created); updated += int(not was_created)

        # ── Membership Plans ─────────────────────────────────────────
        plans_data = [
            {
                'tier': 'starter', 'name': 'Starter',
                'description': 'Entry-level access to the gym floor.',
                'price_monthly_uzs': Decimal('300000'), 'price_monthly_usd': Decimal('24.00'),
                'duration_days': 30,
                'benefits': ['Gym floor access (09:00–18:00)', 'Locker room access', '2 group classes / week'],
            },
            {
                'tier': 'standard', 'name': 'Standard',
                'description': 'Most popular plan — full access with group classes.',
                'price_monthly_uzs': Decimal('500000'), 'price_monthly_usd': Decimal('40.00'),
                'duration_days': 30,
                'benefits': ['Full-day gym access', 'All group classes', 'Sauna access', '1 PT session / month'],
            },
            {
                'tier': 'pro', 'name': 'Pro',
                'description': 'For serious athletes who train daily.',
                'price_monthly_uzs': Decimal('800000'), 'price_monthly_usd': Decimal('64.00'),
                'duration_days': 30,
                'benefits': ['24/7 gym access', 'Unlimited group classes', 'Sauna + pool', '4 PT sessions / month', 'Nutrition plan'],
            },
            {
                'tier': 'vip', 'name': 'VIP',
                'description': 'Premium everything. Dedicated trainer & spa privileges.',
                'price_monthly_uzs': Decimal('1500000'), 'price_monthly_usd': Decimal('120.00'),
                'duration_days': 30,
                'benefits': ['24/7 access', 'Dedicated personal trainer', 'All spa services', 'Meal delivery', 'Recovery services'],
            },
        ]
        for p in plans_data:
            _, was_created = MembershipPlan.objects.update_or_create(
                tier=p['tier'], defaults={**p, 'is_active': True},
            )
            created += int(was_created); updated += int(not was_created)

        # ── Payment Cards ────────────────────────────────────────────
        cards_data = [
            {'bank_name': 'aloqa',      'card_number': '5614688710992099', 'full_name': 'GYM ELITE', 'phone_number': '+998 90 000 00 00'},
            {'bank_name': 'sqb',        'card_number': '8600030442283036', 'full_name': 'GYM ELITE', 'phone_number': '+998 90 000 00 00'},
            {'bank_name': 'visa',       'card_number': '4108590171754990', 'full_name': 'GYM ELITE', 'phone_number': '+998 90 000 00 00'},
            {'bank_name': 'mastercard', 'card_number': '5319517114691874', 'full_name': 'GYM ELITE', 'phone_number': '+998 90 000 00 00'},
        ]
        for c in cards_data:
            _, was_created = PaymentCard.objects.update_or_create(
                card_number=c['card_number'], defaults={**c, 'is_active': True},
            )
            created += int(was_created); updated += int(not was_created)

        # ── Payment Methods ──────────────────────────────────────────
        methods_data = [
            {'method': 'card',   'name': 'Bank Card',  'description': 'Transfer via Uzbek bank card', 'commission_percent': Decimal('0')},
            {'method': 'click',  'name': 'Click',      'description': 'Pay via Click app',           'commission_percent': Decimal('1')},
            {'method': 'payme',  'name': 'Payme',      'description': 'Pay via Payme app',           'commission_percent': Decimal('1')},
            {'method': 'uzum',   'name': 'Uzum Bank',  'description': 'Pay via Uzum Bank',           'commission_percent': Decimal('0')},
        ]
        for m in methods_data:
            _, was_created = PaymentMethod.objects.update_or_create(
                method=m['method'], defaults={**m, 'is_active': True},
            )
            created += int(was_created); updated += int(not was_created)

        # ── Payment Settings (single row) ────────────────────────────
        PaymentSettings.objects.get_or_create(pk=1)

        # ── Discounts ────────────────────────────────────────────────
        now = timezone.now()
        discounts_data = [
            {
                'code': 'NEWYEAR20',
                'description': 'New Year special — 20% off any program',
                'discount_percent': 20, 'discount_uzs': None,
                'valid_from': now, 'valid_until': now + timedelta(days=30),
                'max_uses': 100,
            },
            {
                'code': 'FIRST50',
                'description': 'First-time client? Get 50,000 so‘m off!',
                'discount_percent': 0, 'discount_uzs': Decimal('50000'),
                'valid_from': now, 'valid_until': now + timedelta(days=60),
                'max_uses': None,
            },
        ]
        for d in discounts_data:
            _, was_created = Discount.objects.update_or_create(
                code=d['code'], defaults={**d, 'is_active': True},
            )
            created += int(was_created); updated += int(not was_created)

        # ── Sample schedule ──────────────────────────────────────────
        weight_loss = GymProgram.objects.filter(code='weight_loss').first()
        muscle_gain = GymProgram.objects.filter(code='muscle_gain').first()
        boxing = GymProgram.objects.filter(code='boxing').first()

        from datetime import time
        schedule_data = [
            (weight_loss, 0, time(8, 0),  time(9, 30),  malika),   # Mon 08:00
            (weight_loss, 2, time(8, 0),  time(9, 30),  malika),   # Wed
            (weight_loss, 4, time(8, 0),  time(9, 30),  malika),   # Fri
            (muscle_gain, 1, time(18, 0), time(19, 30), alisher),  # Tue
            (muscle_gain, 3, time(18, 0), time(19, 30), alisher),  # Thu
            (muscle_gain, 5, time(10, 0), time(11, 30), alisher),  # Sat
            (boxing,      0, time(19, 0), time(20, 30), bekzod),   # Mon
            (boxing,      2, time(19, 0), time(20, 30), bekzod),   # Wed
            (boxing,      5, time(17, 0), time(18, 30), bekzod),   # Sat
        ]
        for program, day, start, end, trainer in schedule_data:
            if not program:
                continue
            _, was_created = Schedule.objects.update_or_create(
                program=program, day_of_week=day, start_time=start,
                defaults={'end_time': end, 'trainer': trainer, 'capacity': 20},
            )
            created += int(was_created); updated += int(not was_created)

        self.stdout.write(self.style.SUCCESS(
            f'✅ Seeding complete. {created} created, {updated} updated.'
        ))
