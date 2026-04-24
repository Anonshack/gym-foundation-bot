"""
Info-only menu handlers:
  menu:about, menu:contact, menu:membership, menu:results, menu:nutrition,
  menu:discounts, menu:trainers, menu:schedule
"""
import logging
from pathlib import Path
from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.exceptions import TelegramBadRequest
from django.conf import settings

from bot import services
from bot.keyboards import back_to_menu_keyboard, PROGRAM_ICONS
from bot.utils.i18n import t

logger = logging.getLogger(__name__)
router = Router(name='info')


# ─── About ───────────────────────────────────────────────────────────────────

@router.callback_query(F.data == 'menu:about')
async def cb_about(callback: CallbackQuery, lang: str):
    await _edit(callback, t(lang, 'about_text'), back_to_menu_keyboard(lang))
    await callback.answer()


# ─── Contact ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == 'menu:contact')
async def cb_contact(callback: CallbackQuery, lang: str):
    text = t(lang, 'contact_text', phone=settings.PAYMENT_PHONE)
    await _edit(callback, text, back_to_menu_keyboard(lang))
    await callback.answer()


# ─── Membership plans ────────────────────────────────────────────────────────

TIER_ICONS = {'starter': '🥉', 'standard': '🥈', 'pro': '🥇', 'vip': '👑'}


@router.callback_query(F.data == 'menu:membership')
async def cb_membership(callback: CallbackQuery, lang: str):
    plans = await services.list_membership_plans()
    if not plans:
        await _edit(callback, t(lang, 'no_plans'), back_to_menu_keyboard(lang))
        await callback.answer()
        return

    parts = [t(lang, 'membership_title')]
    for p in plans:
        icon = TIER_ICONS.get(p.tier, '🎁')
        benefits = p.benefits if isinstance(p.benefits, list) else []
        benefits_text = '\n'.join(f'   • {b}' for b in benefits[:6]) if benefits else ''
        parts.append(
            f"\n{icon} <b>{p.name}</b>\n"
            f"💰 {int(p.price_monthly_uzs):,} so‘m / ${p.price_monthly_usd:.2f}\n"
            f"⏱️ {p.duration_days} {'days' if lang == 'en' else ('kun' if lang == 'uz' else 'дней')}\n"
            + (f"{benefits_text}\n" if benefits_text else '')
        )
    await _edit(callback, '\n'.join(parts), back_to_menu_keyboard(lang))
    await callback.answer()


# ─── Results (testimonials) ──────────────────────────────────────────────────

@router.callback_query(F.data == 'menu:results')
async def cb_results(callback: CallbackQuery, lang: str):
    testimonials = await services.list_testimonials()
    if not testimonials:
        await _edit(callback, t(lang, 'no_results'), back_to_menu_keyboard(lang))
        await callback.answer()
        return

    parts = [t(lang, 'results_title'), '']
    for tm in testimonials[:5]:
        stars = '⭐' * tm.rating
        name = tm.user.full_name or 'Anonymous'
        program_name = tm.program.name if tm.program else ''
        parts.append(
            f"{stars}\n"
            f"<b>{name}</b>" + (f" — <i>{program_name}</i>" if program_name else '') + "\n"
            f"💬 {tm.text[:200]}"
            + ('...' if len(tm.text) > 200 else '')
            + '\n'
        )
    await _edit(callback, '\n'.join(parts), back_to_menu_keyboard(lang))
    await callback.answer()


# ─── Nutrition ───────────────────────────────────────────────────────────────

@router.callback_query(F.data == 'menu:nutrition')
async def cb_nutrition(callback: CallbackQuery, lang: str):
    plans = await services.list_nutrition_plans()
    if not plans:
        await _edit(callback, t(lang, 'no_nutrition'), back_to_menu_keyboard(lang))
        await callback.answer()
        return

    parts = [t(lang, 'nutrition_title')]
    for n in plans[:8]:
        parts.append(
            f"\n🍽️ <b>{n.name}</b>\n"
            f"📊 {n.calories} cal  •  P {n.protein_g}g  •  C {n.carbs_g}g  •  F {n.fat_g}g\n"
            f"{n.description[:150]}" + ('...' if len(n.description) > 150 else '')
        )
    await _edit(callback, '\n'.join(parts), back_to_menu_keyboard(lang))
    await callback.answer()


# ─── Discounts ───────────────────────────────────────────────────────────────

@router.callback_query(F.data == 'menu:discounts')
async def cb_discounts(callback: CallbackQuery, lang: str):
    discounts = await services.list_discounts()
    if not discounts:
        await _edit(callback, t(lang, 'no_discounts'), back_to_menu_keyboard(lang))
        await callback.answer()
        return

    parts = [t(lang, 'discounts_title')]
    for d in discounts[:10]:
        value = f"{d.discount_percent}% OFF" if d.discount_percent else f"{int(d.discount_uzs):,} so‘m"
        parts.append(
            f"\n🎁 <b>{d.code}</b>\n"
            f"💥 {value}\n"
            f"📄 {d.description[:140]}\n"
            f"📅 until {d.valid_until.strftime('%Y-%m-%d')}"
        )
    await _edit(callback, '\n'.join(parts), back_to_menu_keyboard(lang))
    await callback.answer()


# ─── Trainers ────────────────────────────────────────────────────────────────

@router.callback_query(F.data == 'menu:trainers')
async def cb_trainers(callback: CallbackQuery, lang: str):
    trainers = await services.list_trainers()
    if not trainers:
        await _edit(callback, t(lang, 'no_trainers'), back_to_menu_keyboard(lang))
        await callback.answer()
        return

    parts = [t(lang, 'trainers_title')]
    for tr in trainers[:10]:
        tg_link = f"@{tr.telegram_username}" if tr.telegram_username else '—'
        parts.append(
            f"\n👨‍🏫 <b>{tr.name}</b>\n"
            f"🎯 {tr.specialization}\n"
            f"🎖️ {tr.experience_years} years experience\n"
            f"📱 {tr.phone}  •  {tg_link}\n"
            f"📝 {tr.bio[:150]}" + ('...' if len(tr.bio) > 150 else '')
        )
    await _edit(callback, '\n'.join(parts), back_to_menu_keyboard(lang))
    await callback.answer()


# ─── Schedule ────────────────────────────────────────────────────────────────

DAY_NAMES = {
    'uz': ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba', 'Yakshanba'],
    'ru': ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'],
    'en': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
}


@router.callback_query(F.data == 'menu:schedule')
async def cb_schedule(callback: CallbackQuery, lang: str):
    schedules = await services.list_schedules()
    if not schedules:
        await _edit(callback, t(lang, 'no_schedule'), back_to_menu_keyboard(lang))
        await callback.answer()
        return

    days = DAY_NAMES.get(lang, DAY_NAMES['en'])
    by_day = {}
    for s in schedules:
        by_day.setdefault(s.day_of_week, []).append(s)

    parts = [t(lang, 'schedule_title')]
    for day_idx in sorted(by_day):
        parts.append(f"\n<b>📅 {days[day_idx]}</b>")
        for s in by_day[day_idx]:
            p_icon = PROGRAM_ICONS.get(s.program.code, '🏋️')
            trainer = f" — {s.trainer.name}" if s.trainer else ''
            parts.append(
                f"   {p_icon} {s.start_time.strftime('%H:%M')}–{s.end_time.strftime('%H:%M')}  "
                f"{s.program.name}{trainer}"
            )
    await _edit(callback, '\n'.join(parts), back_to_menu_keyboard(lang))
    await callback.answer()


# ─── Helper ──────────────────────────────────────────────────────────────────

async def _edit(callback: CallbackQuery, text: str, reply_markup=None):
    """Edit the message; fall back to delete+send on media messages."""
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass
        await callback.message.answer(text, reply_markup=reply_markup)
