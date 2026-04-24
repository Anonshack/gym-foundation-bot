"""
All inline keyboards for the bot.
Callback data convention: <action>:<payload>  (e.g. "lang:uz", "prog:42", "menu:about")
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.utils.i18n import t


# ─── Language selection ──────────────────────────────────────────────────────

def language_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🇺🇿 O'zbek", callback_data="lang:uz")
    kb.button(text="🇷🇺 Русский", callback_data="lang:ru")
    kb.button(text="🇺🇸 English", callback_data="lang:en")
    kb.adjust(2, 1)
    return kb.as_markup()


# ─── Channel subscription ────────────────────────────────────────────────────

def subscription_keyboard(lang: str, channel_url: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, 'subscribe_btn'), url=channel_url)
    kb.button(text=t(lang, 'check_sub_btn'), callback_data="sub:check")
    kb.adjust(1, 1)
    return kb.as_markup()


# ─── Main menu ───────────────────────────────────────────────────────────────

def main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, 'menu_about'),      callback_data="menu:about")
    kb.button(text=t(lang, 'menu_enroll'),     callback_data="menu:enroll")
    kb.button(text=t(lang, 'menu_membership'), callback_data="menu:membership")
    kb.button(text=t(lang, 'menu_contact'),    callback_data="menu:contact")
    kb.button(text=t(lang, 'menu_results'),    callback_data="menu:results")
    kb.button(text=t(lang, 'menu_nutrition'),  callback_data="menu:nutrition")
    kb.button(text=t(lang, 'menu_discounts'),  callback_data="menu:discounts")
    kb.button(text=t(lang, 'menu_ai'),         callback_data="menu:ai")
    kb.button(text=t(lang, 'menu_trainers'),   callback_data="menu:trainers")
    kb.button(text=t(lang, 'menu_schedule'),   callback_data="menu:schedule")
    kb.adjust(1, 1, 2, 2, 2, 2)  # About solo, Enroll solo, then 2-by-2
    return kb.as_markup()


def back_to_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, 'btn_menu'), callback_data="menu:home")
    return kb.as_markup()


# ─── Programs list ──────────────────────────────────────────────────────────

PROGRAM_ICONS = {
    'weight_loss': '⚖️', 'muscle_gain': '💪', 'boxing': '🥊',
    'crossfit': '🏋️', 'personal_training': '👨‍🏫',
    'women_fitness': '👩‍🦰', 'teen_fitness': '🧒',
}


def programs_list_keyboard(lang: str, programs: list) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for p in programs:
        icon = PROGRAM_ICONS.get(p.code, '🏋️')
        kb.button(text=f"{icon} {p.name}", callback_data=f"prog:{p.id}")
    kb.button(text=t(lang, 'btn_menu'), callback_data="menu:home")
    kb.adjust(*([1] * len(programs)), 1)
    return kb.as_markup()


def program_detail_keyboard(lang: str, program_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, 'program_detail_btn_enroll'), callback_data=f"enroll:{program_id}")
    kb.button(text=t(lang, 'btn_back'), callback_data="menu:enroll")
    kb.button(text=t(lang, 'btn_menu'), callback_data="menu:home")
    kb.adjust(1, 2)
    return kb.as_markup()


def payment_confirm_keyboard(lang: str, program_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, 'enroll_understood_btn'), callback_data=f"pay_ok:{program_id}")
    kb.button(text=t(lang, 'btn_back'), callback_data=f"prog:{program_id}")
    kb.adjust(1, 1)
    return kb.as_markup()


# ─── Admin approve/reject (inline buttons on new-payment msg) ────────────────

def admin_payment_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Approve", callback_data=f"adm_app:{payment_id}")
    kb.button(text="❌ Reject",  callback_data=f"adm_rej:{payment_id}")
    kb.adjust(2)
    return kb.as_markup()
