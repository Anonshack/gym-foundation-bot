"""
Enrollment & payment flow:
  menu:enroll  →  programs list
  prog:<id>    →  program detail
  enroll:<id>  →  payment info (cards + rules)
  pay_ok:<id>  →  awaiting screenshot
  <photo>      →  create Payment with screenshot, clear state

A Django post_save signal on Payment fires the admin notification.
"""
import logging
from io import BytesIO

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.exceptions import TelegramBadRequest
from django.conf import settings

from bot import services
from bot.keyboards import (
    programs_list_keyboard, program_detail_keyboard,
    payment_confirm_keyboard, back_to_menu_keyboard,
    PROGRAM_ICONS,
)
from bot.states import EnrollmentFlow
from bot.utils.i18n import t

logger = logging.getLogger(__name__)
router = Router(name='enrollment')


# ─── Programs list ───────────────────────────────────────────────────────────

@router.callback_query(F.data == 'menu:enroll')
async def cb_enroll(callback: CallbackQuery, state: FSMContext, lang: str):
    programs = await services.list_programs()
    if not programs:
        await _edit(callback, t(lang, 'no_programs'), back_to_menu_keyboard(lang))
        await callback.answer()
        return

    await state.set_state(EnrollmentFlow.viewing_programs)
    await _edit(
        callback,
        t(lang, 'enroll_intro'),
        reply_markup=programs_list_keyboard(lang, programs),
    )
    await callback.answer()


# ─── Program detail ──────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith('prog:'))
async def cb_program_detail(callback: CallbackQuery, state: FSMContext, lang: str):
    try:
        program_id = int(callback.data.split(':', 1)[1])
    except ValueError:
        await callback.answer()
        return

    program = await services.get_program(program_id)
    if not program:
        await callback.answer('Program not found', show_alert=True)
        return

    await state.update_data(program_id=program_id)
    await state.set_state(EnrollmentFlow.viewing_program_detail)

    icon = PROGRAM_ICONS.get(program.code, '🏋️')
    benefits = program.get_benefits_list()
    reqs = program.get_requirements_list()

    parts = [
        f"{icon} <b>{program.name}</b>",
        "━━━━━━━━━━━━━━━━━━━━━",
        "",
        f"💰 <b>{int(program.price_uzs):,} so‘m  /  ${program.price_usd:.2f}</b>",
        f"⏱️ {program.duration_days} {'days' if lang == 'en' else ('kun' if lang == 'uz' else 'дней')}",
    ]
    if program.trainer:
        parts.append(f"👨‍🏫 {program.trainer.name}  —  {program.trainer.phone}")
    parts.append('')
    parts.append(f"<i>{program.description}</i>")

    if benefits:
        parts.append('')
        parts.append('<b>✅ Benefits:</b>')
        for b in benefits[:8]:
            parts.append(f'   • {b}')

    if reqs:
        parts.append('')
        parts.append('<b>⚠️ Requirements:</b>')
        for r in reqs[:5]:
            parts.append(f'   • {r}')

    await _edit_or_send(
        callback,
        text='\n'.join(parts),
        reply_markup=program_detail_keyboard(lang, program_id),
        photo=program.image,
    )
    await callback.answer()


# ─── Enroll: show payment info (cards + rules) ───────────────────────────────

@router.callback_query(F.data.startswith('enroll:'))
async def cb_enroll_show_payment(callback: CallbackQuery, state: FSMContext, lang: str):
    try:
        program_id = int(callback.data.split(':', 1)[1])
    except ValueError:
        await callback.answer()
        return

    program = await services.get_program(program_id)
    if not program:
        await callback.answer('Program not found', show_alert=True)
        return

    cards = await services.list_payment_cards()
    if cards:
        cards_text = '\n'.join(
            f"🏦 <b>{c.get_bank_name_display()}</b>\n   <code>{_format_card(c.card_number)}</code>"
            for c in cards
        )
    else:
        # Fallback when admin hasn't configured any cards yet
        cards_text = (
            '<i>Cards are being configured.\n'
            'Please contact admin for payment details.</i>'
        )

    text = t(
        lang, 'enroll_confirm',
        program=program.name,
        price_uzs=f'{int(program.price_uzs):,}',
        price_usd=f'{program.price_usd:.2f}',
        days=program.duration_days,
        cards=cards_text,
        fullname=settings.PAYMENT_FULL_NAME,
        phone=settings.PAYMENT_PHONE,
    )

    await state.update_data(program_id=program_id)
    await state.set_state(EnrollmentFlow.reviewing_payment_info)

    await _edit_or_send(
        callback,
        text=text,
        reply_markup=payment_confirm_keyboard(lang, program_id),
    )
    await callback.answer()


# ─── User confirms: ask for screenshot ───────────────────────────────────────

@router.callback_query(F.data.startswith('pay_ok:'))
async def cb_payment_understood(callback: CallbackQuery, state: FSMContext, lang: str):
    try:
        program_id = int(callback.data.split(':', 1)[1])
    except ValueError:
        await callback.answer()
        return

    await state.update_data(program_id=program_id)
    await state.set_state(EnrollmentFlow.awaiting_screenshot)

    await _edit(
        callback,
        text=t(lang, 'send_screenshot_prompt'),
        reply_markup=back_to_menu_keyboard(lang),
    )
    await callback.answer()


# ─── Screenshot upload ───────────────────────────────────────────────────────

@router.message(EnrollmentFlow.awaiting_screenshot, F.photo)
async def on_screenshot(message: Message, bot: Bot, state: FSMContext, lang: str):
    data = await state.get_data()
    program_id = data.get('program_id')
    if not program_id:
        await message.answer(t(lang, 'error_generic'), reply_markup=back_to_menu_keyboard(lang))
        await state.clear()
        return

    # Pick the highest-resolution photo
    photo = message.photo[-1]

    try:
        file = await bot.get_file(photo.file_id)
        buf = BytesIO()
        await bot.download_file(file.file_path, destination=buf)
        buf.seek(0)
        file_bytes = buf.read()
    except Exception as e:
        logger.error(f'Failed to download screenshot: {e}')
        await message.answer(t(lang, 'error_generic'), reply_markup=back_to_menu_keyboard(lang))
        return

    try:
        payment = await services.create_payment_with_screenshot(
            telegram_id=message.from_user.id,
            program_id=program_id,
            file_bytes=file_bytes,
            filename=f'{message.from_user.id}_{photo.file_id}.jpg',
        )
        logger.info(f'Created payment #{payment.id} for user {message.from_user.id}')
    except Exception as e:
        logger.exception('Failed to create payment')
        await message.answer(t(lang, 'error_generic'), reply_markup=back_to_menu_keyboard(lang))
        return

    await state.clear()
    await message.answer(
        t(lang, 'screenshot_received'),
        reply_markup=back_to_menu_keyboard(lang),
    )


@router.message(EnrollmentFlow.awaiting_screenshot)
async def on_not_photo(message: Message, lang: str):
    await message.answer(t(lang, 'only_photo'))


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _format_card(number: str) -> str:
    """Format card number in groups of 4 digits."""
    digits = ''.join(ch for ch in number if ch.isdigit())
    return ' '.join(digits[i:i + 4] for i in range(0, len(digits), 4)) or number


async def _edit(callback: CallbackQuery, text: str, reply_markup=None):
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass
        await callback.message.answer(text, reply_markup=reply_markup)


async def _edit_or_send(callback: CallbackQuery, text: str, reply_markup=None, photo=None):
    """
    If the program has an image file and the current message has no photo,
    replace the text message with a photo + caption message.
    """
    has_photo = photo and hasattr(photo, 'path')
    if has_photo:
        from aiogram.types import FSInputFile
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass
        try:
            await callback.message.answer_photo(
                FSInputFile(photo.path),
                caption=text[:1024],  # Telegram caption limit
                reply_markup=reply_markup,
            )
            if len(text) > 1024:
                await callback.message.answer(text[1024:], reply_markup=reply_markup)
            return
        except Exception as e:
            logger.warning(f'Failed to send with photo: {e}. Falling back to text.')
    # text-only fallback
    await _edit(callback, text, reply_markup)
