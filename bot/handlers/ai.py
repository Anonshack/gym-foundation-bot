"""
Simple rule-based AI fitness assistant.
No external API needed — matches keywords and returns curated answers.
Set OPENAI_API_KEY in .env to (optionally) upgrade to real AI — see _maybe_call_openai.
"""
import logging
import os

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards import back_to_menu_keyboard
from bot.states import AIFlow
from bot.utils.i18n import t

logger = logging.getLogger(__name__)
router = Router(name='ai')


# ─── Open the AI chat ────────────────────────────────────────────────────────

@router.callback_query(F.data == 'menu:ai')
async def cb_ai_open(callback: CallbackQuery, state: FSMContext, lang: str):
    await state.set_state(AIFlow.awaiting_question)
    try:
        await callback.message.edit_text(
            t(lang, 'ai_welcome'),
            reply_markup=back_to_menu_keyboard(lang),
        )
    except Exception:
        await callback.message.answer(
            t(lang, 'ai_welcome'),
            reply_markup=back_to_menu_keyboard(lang),
        )
    await callback.answer()


# ─── Receive a question ──────────────────────────────────────────────────────

@router.message(AIFlow.awaiting_question, F.text)
async def on_ai_question(message: Message, lang: str):
    question = (message.text or '').strip()
    if not question:
        return

    thinking = await message.answer(t(lang, 'ai_thinking'))

    answer = _maybe_call_openai(question, lang) or _rule_based_answer(question, lang)

    try:
        await thinking.edit_text(answer, reply_markup=back_to_menu_keyboard(lang))
    except Exception:
        await message.answer(answer, reply_markup=back_to_menu_keyboard(lang))


# ─── Optional OpenAI integration (only if OPENAI_API_KEY is set) ─────────────

def _maybe_call_openai(question: str, lang: str):
    api_key = os.environ.get('OPENAI_API_KEY') or ''
    if not api_key:
        return None
    try:
        import requests
        lang_name = {'uz': "Uzbek", 'ru': 'Russian', 'en': 'English'}.get(lang, 'English')
        resp = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
            json={
                'model': 'gpt-4o-mini',
                'messages': [
                    {'role': 'system', 'content': f'You are a friendly fitness assistant. Answer in {lang_name}. Keep answers short (120 words).'},
                    {'role': 'user', 'content': question},
                ],
                'max_tokens': 300,
                'temperature': 0.7,
            },
            timeout=20,
        )
        if resp.status_code == 200:
            return '🤖 ' + resp.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        logger.warning(f'OpenAI call failed, falling back to rules: {e}')
    return None


# ─── Rule-based fallback ─────────────────────────────────────────────────────

_KEYWORDS = {
    # keyword_group : (uz_answer, ru_answer, en_answer)
    ('protein', 'oqsil', 'белок'): (
        "🥩 <b>Oqsil haqida</b>\n\n"
        "Haftasiga 1 kg tana og‘irligiga 1.6–2.2g oqsil kerak.\n"
        "Yaxshi manbalar: tovuq, baliq, tuxum, sut mahsulotlari, loviya.\n"
        "Har bir ovqatda 20–40g oqsil oling.",
        "🥩 <b>О белке</b>\n\n"
        "Нужно 1.6–2.2 г белка на 1 кг веса в день.\n"
        "Лучшие источники: курица, рыба, яйца, молочные продукты, бобовые.\n"
        "Принимайте 20–40 г белка за приём пищи.",
        "🥩 <b>About protein</b>\n\n"
        "You need 1.6–2.2 g of protein per kg of body weight daily.\n"
        "Best sources: chicken, fish, eggs, dairy, legumes.\n"
        "Aim for 20–40 g of protein per meal.",
    ),
    ('weight', 'vazn', 'похуд', 'вес'): (
        "⚖️ <b>Vazn yo‘qotish</b>\n\n"
        "1) Kuniga 300–500 kkal kamroq yeng.\n"
        "2) Haftasiga 3–4 marta kuch mashqlari.\n"
        "3) Kuniga 8000+ qadam.\n"
        "4) Oqsil ko‘p, qand kam.\n"
        "5) 7+ soat uyqu.\n\n"
        "Sekin va barqaror — eng yaxshi yo‘l.",
        "⚖️ <b>Похудение</b>\n\n"
        "1) Ешьте на 300–500 ккал меньше в день.\n"
        "2) Силовые тренировки 3–4 раза в неделю.\n"
        "3) 8000+ шагов в день.\n"
        "4) Больше белка, меньше сахара.\n"
        "5) 7+ часов сна.\n\n"
        "Медленно, но стабильно — это лучший путь.",
        "⚖️ <b>Weight loss</b>\n\n"
        "1) Eat 300–500 kcal less daily.\n"
        "2) 3–4 strength workouts a week.\n"
        "3) 8000+ steps per day.\n"
        "4) More protein, less sugar.\n"
        "5) 7+ hours of sleep.\n\n"
        "Slow and steady wins.",
    ),
    ('muscle', 'mushak', 'muscles', 'мышц'): (
        "💪 <b>Mushak o‘stirish</b>\n\n"
        "• Haftasiga 3–5 marta og‘irlik bilan mashq\n"
        "• Har mashqda 8–12 takror, 3–4 sonda\n"
        "• Progressiv yuklama (og‘irlikni oshiring)\n"
        "• 1.6–2.2g oqsil har kg tana og‘irligi\n"
        "• Kaloriyadan 10–20% ko‘p yeng\n"
        "• 7–8 soat uyqu — mushak shunda o‘sadi",
        "💪 <b>Набор мышц</b>\n\n"
        "• Силовые 3–5 раз в неделю\n"
        "• 8–12 повторений, 3–4 подхода\n"
        "• Прогрессивная нагрузка\n"
        "• 1.6–2.2 г белка на кг веса\n"
        "• +10–20% калорий\n"
        "• 7–8 часов сна — мышцы растут во сне",
        "💪 <b>Muscle gain</b>\n\n"
        "• Strength train 3–5× per week\n"
        "• 8–12 reps × 3–4 sets\n"
        "• Progressive overload\n"
        "• 1.6–2.2 g protein per kg bodyweight\n"
        "• Eat 10–20% above maintenance calories\n"
        "• 7–8 hours sleep — muscles grow during rest",
    ),
    ('cardio', 'yugur', 'бег', 'кардио', 'running'): (
        "🏃 <b>Kardio</b>\n\n"
        "• Haftasiga 150 daqiqa o‘rtacha yoki 75 daq kuchli kardio\n"
        "• Yugurish, velosiped, suzish — tanlang\n"
        "• Qalb uchun sog‘lom, kaloriya yoqadi\n"
        "• Mushak ham yo‘qotmaslik uchun kuch mashqlari bilan qo‘shing",
        "🏃 <b>Кардио</b>\n\n"
        "• 150 мин умеренного или 75 мин интенсивного кардио в неделю\n"
        "• Бег, велосипед, плавание — на выбор\n"
        "• Полезно для сердца, сжигает калории\n"
        "• Сочетайте с силовыми, чтобы не терять мышцы",
        "🏃 <b>Cardio</b>\n\n"
        "• 150 min of moderate or 75 min of intense cardio per week\n"
        "• Running, cycling, swimming — your choice\n"
        "• Heart-healthy and burns calories\n"
        "• Combine with strength training to keep muscle",
    ),
    ('water', 'suv', 'вода'): (
        "💧 <b>Suv</b>\n\n"
        "Kuniga 2.5–3 litr suv iching.\n"
        "Mashq qilganda qo‘shimcha 500 ml.\n"
        "Mashqdan oldin 30 daq davomida 1 stakan.",
        "💧 <b>Вода</b>\n\n"
        "Пейте 2.5–3 литра воды в день.\n"
        "На тренировке — дополнительно 500 мл.\n"
        "За 30 мин до тренировки — 1 стакан.",
        "💧 <b>Water</b>\n\n"
        "Drink 2.5–3 litres a day.\n"
        "Add 500 ml during workouts.\n"
        "Drink a glass 30 min before exercise.",
    ),
    ('sleep', 'uyqu', 'сон'): (
        "😴 <b>Uyqu</b>\n\n"
        "Har kuni 7–9 soat uxlang.\n"
        "Yetarlicha uxlamaslik:\n"
        "• Mushak kam o‘sadi\n"
        "• Yog‘ saqlaydi\n"
        "• Energiya kam bo‘ladi",
        "😴 <b>Сон</b>\n\n"
        "Спите 7–9 часов в сутки.\n"
        "Мало сна:\n"
        "• Мышцы растут хуже\n"
        "• Жир держится\n"
        "• Меньше энергии",
        "😴 <b>Sleep</b>\n\n"
        "Sleep 7–9 hours per night.\n"
        "Not enough sleep means:\n"
        "• Slower muscle growth\n"
        "• Harder fat loss\n"
        "• Lower energy",
    ),
}


def _rule_based_answer(question: str, lang: str) -> str:
    q = question.lower()
    lang_idx = {'uz': 0, 'ru': 1, 'en': 2}.get(lang, 2)
    for keywords, answers in _KEYWORDS.items():
        if any(k in q for k in keywords):
            return '🤖 ' + answers[lang_idx]

    fallback = {
        'uz': (
            "🤖 Savolingiz qiziqarli! Men fitness, ovqatlanish va "
            "mashqlar bo‘yicha savollarga javob beraman.\n\n"
            "Masalan: <i>oqsil, vazn, mushak, kardio, suv, uyqu</i> "
            "kabi mavzularni bering."
        ),
        'ru': (
            "🤖 Интересный вопрос! Я отвечаю о фитнесе, питании "
            "и тренировках.\n\n"
            "Например: <i>белок, вес, мышцы, кардио, вода, сон</i> — "
            "спросите об этом!"
        ),
        'en': (
            "🤖 Great question! I can help with fitness, nutrition "
            "and workouts.\n\n"
            "Try asking about: <i>protein, weight, muscle, cardio, water, sleep</i>."
        ),
    }
    return fallback.get(lang, fallback['en'])
