"""
All multilingual texts for the bot.
Usage:  t(lang, 'welcome')  →  returns translated string
"""

TEXTS = {
    'uz': {
        # ── Welcome / Language ─────────────────────────────────────
        'welcome': (
            "🏋️ <b>GYM ELITE</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Xush kelibsiz! Bu yerda siz:\n"
            "💪 Professional trenerlar bilan ishlaysiz\n"
            "🥇 Zamonaviy asbob-uskunalarga ega bo‘lasiz\n"
            "📊 Shaxsiy dasturingizni tuzasiz\n"
            "🎯 Natijaga erishasiz\n\n"
            "🌐 Iltimos, tilni tanlang 👇"
        ),
        'language_selected': "✅ Til tanlandi!",
        'choose_lang': "🌐 Tilni tanlang:",

        # ── Subscription ───────────────────────────────────────────
        'subscribe_title': (
            "📢 <b>Kanalga obuna bo‘ling</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Botdan foydalanish uchun\n"
            "kanalimizga a‘zo bo‘ling.\n\n"
            "Kanalda har kuni:\n"
            "• Yangiliklar va aksiyalar\n"
            "• Mashq maslahatlari\n"
            "• Ovqatlanish retseptlari\n\n"
            "A‘zo bo‘lganidan keyin\n"
            "👇 Tekshirish tugmasini bosing"
        ),
        'subscribe_btn': "📢 Kanalga o‘tish",
        'check_sub_btn': "✅ Tekshirish",
        'not_subscribed': (
            "❌ <b>Siz hali obuna bo‘lmagansiz</b>\n\n"
            "Iltimos, avval kanalga o‘ting va\n"
            "qayta Tekshirish tugmasini bosing."
        ),
        'subscribed_ok': "✅ Ajoyib! Rahmat 💪",

        # ── Main menu ──────────────────────────────────────────────
        'main_menu': (
            "🏠 <b>ASOSIY MENYU</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Quyidagi bo‘limdan birini tanlang 👇"
        ),
        'menu_about':      "🏋️ Biz haqimizda",
        'menu_enroll':     "📝 Kursga yozilish",
        'menu_membership': "💪 Trening paketlari",
        'menu_contact':    "📍 Manzil va aloqa",
        'menu_results':    "📸 Mijozlar natijalari",
        'menu_nutrition':  "🥗 Ovqatlanish",
        'menu_discounts':  "🎁 Aksiyalar",
        'menu_ai':         "🤖 AI yordamchi",
        'menu_trainers':   "⭐ Trenerlar",
        'menu_schedule':   "📅 Jadval",
        'btn_back':        "◀️ Ortga",
        'btn_menu':        "🏠 Menyu",

        # ── About ──────────────────────────────────────────────────
        'about_text': (
            "🏆 <b>GYM ELITE HAQIDA</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Biz 10+ yillik tajribaga ega\n"
            "professional fitnes markaziymiz.\n\n"
            "📊 <b>Bizning natijalar:</b>\n"
            "✅ 5000+ muvaffaqiyatli mijoz\n"
            "✅ 20+ sertifikatli trener\n"
            "✅ Zamonaviy asboblar\n"
            "✅ 100% natija kafolati\n\n"
            "💪 <b>Biz taklif qilamiz:</b>\n"
            "🏋️ Professional trenerlar\n"
            "📱 Online coaching\n"
            "🥗 Ovqatlanish rejalari\n"
            "📊 Progress kuzatuv\n"
            "🏅 Shaxsiy dasturlar"
        ),

        # ── Contact ────────────────────────────────────────────────
        'contact_text': (
            "📍 <b>MANZIL VA ALOQA</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📞 <b>Telefon:</b> {phone}\n"
            "🕐 <b>Ish vaqti:</b> 09:00 – 21:00\n"
            "📅 <b>Kunlar:</b> Du – Sha (6 kun)\n\n"
            "📍 <b>Manzil:</b>\n"
            "Toshkent shahri,\n"
            "Yunusobod tumani, 10-mavze\n\n"
            "Biz sizni kutamiz! 💪"
        ),

        # ── Programs / Enroll ──────────────────────────────────────
        'enroll_intro': (
            "📝 <b>KURSGA YOZILISH</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "O‘zingizga mos dasturni tanlang 👇"
        ),
        'no_programs': "❌ Hozircha faol dasturlar mavjud emas. Tez orada qo‘shamiz!",
        'program_detail_btn_enroll': "✅ Shu dasturga yozilish",
        'enroll_confirm': (
            "💳 <b>TO‘LOV MA‘LUMOTLARI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<b>Dastur:</b> {program}\n"
            "<b>Narx:</b> {price_uzs} so‘m / ${price_usd}\n"
            "<b>Davomiyligi:</b> {days} kun\n\n"
            "💳 <b>To‘lov uchun kartalar:</b>\n\n"
            "{cards}\n\n"
            "👤 <b>F.I.O:</b> {fullname}\n"
            "📞 <b>Telefon:</b> {phone}\n\n"
            "⚠️ <b>DIQQAT:</b>\n"
            "To‘lov qilganingizdan so‘ng, screenshot (chek rasmi)\n"
            "yuboring. Noto‘g‘ri rasm yuborsangiz bloklanishingiz mumkin!"
        ),
        'enroll_understood_btn': "✅ Tushundim, chek yuboraman",
        'send_screenshot_prompt': (
            "📸 <b>To‘lov chekini yuboring</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Iltimos, to‘lov screenshotini\n"
            "rasm (photo) sifatida yuboring."
        ),
        'only_photo': "❌ Iltimos, faqat rasm (photo) yuboring!",
        'screenshot_received': (
            "✅ <b>Rasm qabul qilindi</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "To‘lovingiz tekshirilmoqda.\n"
            "Menejerlarimiz tez orada siz bilan\n"
            "bog‘lanishadi va natijani xabar qilishadi.\n\n"
            "Iltimos, biroz kuting 💪"
        ),

        # ── Membership ─────────────────────────────────────────────
        'membership_title': (
            "💪 <b>A‘ZOLIK PAKETLARI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Biz uchun eng mos paketni tanlang 👇"
        ),
        'no_plans': "❌ Hozircha paketlar qo‘shilmagan.",

        # ── Results ────────────────────────────────────────────────
        'results_title': (
            "📸 <b>MIJOZLARIMIZ NATIJALARI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Ular uddaladi — siz ham uddalaysiz! 💪"
        ),
        'no_results': "📸 Hozircha natijalar ulashilmagan.\nBirinchi bo‘lib o‘z natijangizni baham ko‘ring!",

        # ── Nutrition ──────────────────────────────────────────────
        'nutrition_title': (
            "🥗 <b>OVQATLANISH REJALARI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Sog‘lom va mazali ratsionlar 👇"
        ),
        'no_nutrition': "❌ Hozircha ovqatlanish rejalari qo‘shilmagan.",

        # ── Discounts ──────────────────────────────────────────────
        'discounts_title': (
            "🎁 <b>AKSIYALAR VA CHEGIRMALAR</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
        ),
        'no_discounts': "😊 Hozircha aktiv aksiyalar yo‘q.\nTez orada foydali takliflar bilan qaytamiz!",

        # ── AI ─────────────────────────────────────────────────────
        'ai_welcome': (
            "🤖 <b>AI FITNES YORDAMCHI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Fitness, ovqatlanish yoki mashqlar\n"
            "haqida istalgan savolingizni bering.\n\n"
            "Masalan:\n"
            "• Qanday mashq qilish kerak?\n"
            "• Qancha ovqat yeyish kerak?\n"
            "• Oqsil qanday olish mumkin?\n\n"
            "Savolingizni yozing 👇"
        ),
        'ai_thinking': "🤖 O‘ylayapman...",

        # ── Trainers ───────────────────────────────────────────────
        'trainers_title': (
            "⭐ <b>BIZNING TRENERLAR</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Professional sertifikatli trenerlar 👇"
        ),
        'no_trainers': "❌ Hozircha trenerlar ro‘yxati mavjud emas.",

        # ── Schedule ───────────────────────────────────────────────
        'schedule_title': (
            "📅 <b>MASHG‘ULOTLAR JADVALI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
        ),
        'no_schedule': "❌ Hozircha jadval qo‘shilmagan.",

        # ── Blocked / errors ───────────────────────────────────────
        'blocked': "🚫 Siz bloklangansiz. Admin bilan bog‘laning.",
        'error_generic': "❌ Xatolik yuz berdi. Qayta urinib ko‘ring.",
    },

    'ru': {
        'welcome': (
            "🏋️ <b>GYM ELITE</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Добро пожаловать! Здесь вы:\n"
            "💪 Работаете с профессионалами\n"
            "🥇 Используете современные тренажёры\n"
            "📊 Получаете свою программу\n"
            "🎯 Достигаете результата\n\n"
            "🌐 Выберите язык 👇"
        ),
        'language_selected': "✅ Язык выбран!",
        'choose_lang': "🌐 Выберите язык:",

        'subscribe_title': (
            "📢 <b>Подпишитесь на канал</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Чтобы пользоваться ботом,\n"
            "подпишитесь на наш канал.\n\n"
            "В канале ежедневно:\n"
            "• Новости и акции\n"
            "• Советы по тренировкам\n"
            "• Рецепты питания\n\n"
            "После подписки нажмите 👇\n"
            "кнопку Проверить."
        ),
        'subscribe_btn': "📢 Перейти в канал",
        'check_sub_btn': "✅ Проверить",
        'not_subscribed': (
            "❌ <b>Вы ещё не подписались</b>\n\n"
            "Сначала перейдите в канал и\n"
            "нажмите Проверить снова."
        ),
        'subscribed_ok': "✅ Отлично! Спасибо 💪",

        'main_menu': (
            "🏠 <b>ГЛАВНОЕ МЕНЮ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Выберите раздел 👇"
        ),
        'menu_about':      "🏋️ О нас",
        'menu_enroll':     "📝 Записаться",
        'menu_membership': "💪 Пакеты",
        'menu_contact':    "📍 Адрес и контакт",
        'menu_results':    "📸 Результаты клиентов",
        'menu_nutrition':  "🥗 Питание",
        'menu_discounts':  "🎁 Акции",
        'menu_ai':         "🤖 AI помощник",
        'menu_trainers':   "⭐ Тренеры",
        'menu_schedule':   "📅 Расписание",
        'btn_back':        "◀️ Назад",
        'btn_menu':        "🏠 Меню",

        'about_text': (
            "🏆 <b>О GYM ELITE</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Мы — профессиональный фитнес-центр\n"
            "с опытом более 10 лет.\n\n"
            "📊 <b>Наши достижения:</b>\n"
            "✅ 5000+ успешных клиентов\n"
            "✅ 20+ сертифицированных тренеров\n"
            "✅ Современное оборудование\n"
            "✅ 100% гарантия результата\n\n"
            "💪 <b>Мы предлагаем:</b>\n"
            "🏋️ Профессиональных тренеров\n"
            "📱 Онлайн-коучинг\n"
            "🥗 Планы питания\n"
            "📊 Отслеживание прогресса\n"
            "🏅 Индивидуальные программы"
        ),

        'contact_text': (
            "📍 <b>АДРЕС И КОНТАКТЫ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📞 <b>Телефон:</b> {phone}\n"
            "🕐 <b>Часы работы:</b> 09:00 – 21:00\n"
            "📅 <b>Дни:</b> Пн – Сб (6 дней)\n\n"
            "📍 <b>Адрес:</b>\n"
            "г. Ташкент, Юнусабадский р-н,\n"
            "10-й квартал\n\n"
            "Ждём вас! 💪"
        ),

        'enroll_intro': (
            "📝 <b>ЗАПИСЬ НА КУРС</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Выберите подходящую программу 👇"
        ),
        'no_programs': "❌ Пока нет активных программ. Скоро добавим!",
        'program_detail_btn_enroll': "✅ Записаться на эту программу",
        'enroll_confirm': (
            "💳 <b>ДЕТАЛИ ОПЛАТЫ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<b>Программа:</b> {program}\n"
            "<b>Цена:</b> {price_uzs} сум / ${price_usd}\n"
            "<b>Длительность:</b> {days} дней\n\n"
            "💳 <b>Карты для оплаты:</b>\n\n"
            "{cards}\n\n"
            "👤 <b>Ф.И.О:</b> {fullname}\n"
            "📞 <b>Телефон:</b> {phone}\n\n"
            "⚠️ <b>ВНИМАНИЕ:</b>\n"
            "После оплаты отправьте скриншот чека.\n"
            "За неверное изображение можно получить бан!"
        ),
        'enroll_understood_btn': "✅ Понял, отправляю чек",
        'send_screenshot_prompt': (
            "📸 <b>Отправьте скриншот оплаты</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Пожалуйста, отправьте скриншот\n"
            "как фотографию."
        ),
        'only_photo': "❌ Отправьте только изображение!",
        'screenshot_received': (
            "✅ <b>Скриншот принят</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Ваш платёж проверяется.\n"
            "Менеджеры свяжутся с вами в ближайшее\n"
            "время и сообщат результат.\n\n"
            "Пожалуйста, подождите 💪"
        ),

        'membership_title': (
            "💪 <b>ПАКЕТЫ АБОНЕМЕНТА</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Выберите подходящий пакет 👇"
        ),
        'no_plans': "❌ Пакеты пока не добавлены.",

        'results_title': (
            "📸 <b>РЕЗУЛЬТАТЫ НАШИХ КЛИЕНТОВ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Они справились — справитесь и вы! 💪"
        ),
        'no_results': "📸 Пока никто не поделился.\nБудьте первым!",

        'nutrition_title': (
            "🥗 <b>ПЛАНЫ ПИТАНИЯ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Полезные и вкусные рационы 👇"
        ),
        'no_nutrition': "❌ Планов питания пока нет.",

        'discounts_title': (
            "🎁 <b>АКЦИИ И СКИДКИ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
        ),
        'no_discounts': "😊 Активных акций пока нет.\nСкоро будут интересные предложения!",

        'ai_welcome': (
            "🤖 <b>AI ФИТНЕС-ПОМОЩНИК</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Задайте любой вопрос о фитнесе,\n"
            "питании или тренировках.\n\n"
            "Например:\n"
            "• Как правильно тренироваться?\n"
            "• Сколько нужно есть?\n"
            "• Как получать белок?\n\n"
            "Напишите ваш вопрос 👇"
        ),
        'ai_thinking': "🤖 Думаю...",

        'trainers_title': (
            "⭐ <b>НАШИ ТРЕНЕРЫ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Сертифицированные профессионалы 👇"
        ),
        'no_trainers': "❌ Список тренеров пока пуст.",

        'schedule_title': (
            "📅 <b>РАСПИСАНИЕ ЗАНЯТИЙ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
        ),
        'no_schedule': "❌ Расписание ещё не добавлено.",

        'blocked': "🚫 Вы заблокированы. Свяжитесь с администратором.",
        'error_generic': "❌ Произошла ошибка. Попробуйте ещё раз.",
    },

    'en': {
        'welcome': (
            "🏋️ <b>GYM ELITE</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Welcome! Here you will:\n"
            "💪 Train with professional coaches\n"
            "🥇 Use modern equipment\n"
            "📊 Get your personal program\n"
            "🎯 Reach your goals\n\n"
            "🌐 Please choose your language 👇"
        ),
        'language_selected': "✅ Language selected!",
        'choose_lang': "🌐 Choose language:",

        'subscribe_title': (
            "📢 <b>Subscribe to our channel</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "To use the bot, please\n"
            "subscribe to our channel.\n\n"
            "Daily in the channel:\n"
            "• News and offers\n"
            "• Workout tips\n"
            "• Nutrition recipes\n\n"
            "After subscribing, tap 👇\n"
            "the Check button below."
        ),
        'subscribe_btn': "📢 Go to channel",
        'check_sub_btn': "✅ Check",
        'not_subscribed': (
            "❌ <b>You are not subscribed yet</b>\n\n"
            "Please join the channel first, then\n"
            "tap Check again."
        ),
        'subscribed_ok': "✅ Great! Thank you 💪",

        'main_menu': (
            "🏠 <b>MAIN MENU</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Choose a section below 👇"
        ),
        'menu_about':      "🏋️ About us",
        'menu_enroll':     "📝 Join program",
        'menu_membership': "💪 Membership plans",
        'menu_contact':    "📍 Location & contact",
        'menu_results':    "📸 Client results",
        'menu_nutrition':  "🥗 Nutrition",
        'menu_discounts':  "🎁 Discounts",
        'menu_ai':         "🤖 AI assistant",
        'menu_trainers':   "⭐ Trainers",
        'menu_schedule':   "📅 Schedule",
        'btn_back':        "◀️ Back",
        'btn_menu':        "🏠 Menu",

        'about_text': (
            "🏆 <b>ABOUT GYM ELITE</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "We are a professional fitness center\n"
            "with 10+ years of experience.\n\n"
            "📊 <b>Our results:</b>\n"
            "✅ 5000+ successful clients\n"
            "✅ 20+ certified trainers\n"
            "✅ Modern equipment\n"
            "✅ 100% result guarantee\n\n"
            "💪 <b>We offer:</b>\n"
            "🏋️ Professional trainers\n"
            "📱 Online coaching\n"
            "🥗 Nutrition plans\n"
            "📊 Progress tracking\n"
            "🏅 Personalized programs"
        ),

        'contact_text': (
            "📍 <b>LOCATION & CONTACT</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📞 <b>Phone:</b> {phone}\n"
            "🕐 <b>Hours:</b> 09:00 – 21:00\n"
            "📅 <b>Days:</b> Mon – Sat (6 days)\n\n"
            "📍 <b>Address:</b>\n"
            "Tashkent city,\n"
            "Yunusabad district, 10-block\n\n"
            "We are waiting for you! 💪"
        ),

        'enroll_intro': (
            "📝 <b>JOIN PROGRAM</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Choose the program that suits you 👇"
        ),
        'no_programs': "❌ No active programs right now. Coming soon!",
        'program_detail_btn_enroll': "✅ Enroll in this program",
        'enroll_confirm': (
            "💳 <b>PAYMENT DETAILS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "<b>Program:</b> {program}\n"
            "<b>Price:</b> {price_uzs} UZS / ${price_usd}\n"
            "<b>Duration:</b> {days} days\n\n"
            "💳 <b>Cards for payment:</b>\n\n"
            "{cards}\n\n"
            "👤 <b>Full name:</b> {fullname}\n"
            "📞 <b>Phone:</b> {phone}\n\n"
            "⚠️ <b>IMPORTANT:</b>\n"
            "After paying, send your screenshot.\n"
            "Sending wrong images may get you banned!"
        ),
        'enroll_understood_btn': "✅ Understood, sending screenshot",
        'send_screenshot_prompt': (
            "📸 <b>Send payment screenshot</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Please send the screenshot\n"
            "as a photo."
        ),
        'only_photo': "❌ Please send a photo only!",
        'screenshot_received': (
            "✅ <b>Screenshot received</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Your payment is being reviewed.\n"
            "Our managers will contact you soon\n"
            "with the result.\n\n"
            "Please wait 💪"
        ),

        'membership_title': (
            "💪 <b>MEMBERSHIP PLANS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Choose the plan that suits you 👇"
        ),
        'no_plans': "❌ No plans added yet.",

        'results_title': (
            "📸 <b>OUR CLIENTS' RESULTS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "They did it — so can you! 💪"
        ),
        'no_results': "📸 No shared results yet.\nBe the first!",

        'nutrition_title': (
            "🥗 <b>NUTRITION PLANS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Healthy and tasty meal plans 👇"
        ),
        'no_nutrition': "❌ No nutrition plans yet.",

        'discounts_title': (
            "🎁 <b>DISCOUNTS & OFFERS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
        ),
        'no_discounts': "😊 No active discounts right now.\nStay tuned for great offers soon!",

        'ai_welcome': (
            "🤖 <b>AI FITNESS ASSISTANT</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Ask anything about fitness,\n"
            "nutrition or exercise.\n\n"
            "For example:\n"
            "• How should I train?\n"
            "• How much should I eat?\n"
            "• How to get enough protein?\n\n"
            "Write your question 👇"
        ),
        'ai_thinking': "🤖 Thinking...",

        'trainers_title': (
            "⭐ <b>OUR TRAINERS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Certified professionals 👇"
        ),
        'no_trainers': "❌ No trainers listed yet.",

        'schedule_title': (
            "📅 <b>CLASS SCHEDULE</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
        ),
        'no_schedule': "❌ Schedule not added yet.",

        'blocked': "🚫 You are blocked. Please contact the admin.",
        'error_generic': "❌ An error occurred. Please try again.",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    """Fetch localized text. Falls back to English, then key name."""
    lang = lang if lang in TEXTS else 'en'
    text = TEXTS[lang].get(key) or TEXTS['en'].get(key) or f'[{key}]'
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text
