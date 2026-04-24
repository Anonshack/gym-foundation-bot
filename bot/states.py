"""FSM state groups for the bot."""
from aiogram.fsm.state import State, StatesGroup


class UserFlow(StatesGroup):
    choosing_language = State()
    checking_subscription = State()
    in_main_menu = State()


class EnrollmentFlow(StatesGroup):
    viewing_programs = State()
    viewing_program_detail = State()
    reviewing_payment_info = State()
    awaiting_screenshot = State()


class AIFlow(StatesGroup):
    awaiting_question = State()
