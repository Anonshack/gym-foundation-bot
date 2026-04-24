# 🏋️ Gym Elite — Telegram Bot + Django CRM

A production-ready gym management system: **Aiogram 3 Telegram bot** + **Django 5 admin panel**.
Full trilingual support (🇺🇿 Uzbek / 🇷🇺 Russian / 🇺🇸 English), program enrollment, payment
screenshots, and Telegram-based approve/reject flow.

---

## ✨ Features

### 🤖 Bot
- `/start` → language selection → channel subscription check → main menu
- **10 menu sections**, all fully functional:
  - 🏋️ About us • 📝 Join program • 💪 Membership plans • 📍 Location & contact
  - 📸 Client results • 🥗 Nutrition plans • 🎁 Discounts • 🤖 AI assistant
  - ⭐ Trainers • 📅 Schedule
- **Enrollment flow**: pick program → see details → view payment cards → upload screenshot
- **AI fitness assistant** — rule-based by default, upgradeable to OpenAI with one env var
- Channel subscription enforcement
- Blocked-user middleware
- Multilingual throughout

### 🎛️ Admin panel (Django + Jazzmin)
- **Dark, sidebar-indexed premium theme**
- Payments admin with:
  - Screenshot preview inline
  - One-click **Approve / Reject** buttons that **notify the user on Telegram**
  - Colour-coded status badges, payment type badges, action history
- Trainer avatars, program icons, progress bars on enrollments
- Block/unblock users in 1 click
- Seed command populates demo content

### 🔔 Real-time admin notifications
- New payment → screenshot + info sent to the admin group with inline
  **Approve / Reject** buttons. Tapping either updates the payment and notifies
  the user in their language. No Celery / Redis required.

---

## 🚀 Quick Start (3 minutes, zero database setup)

### 1. Install dependencies

```bash
python -m venv venv
source venv/bin/activate         # Linux/Mac
# venv\Scripts\activate          # Windows

pip install -r requirements.txt
```

### 2. Configure `.env`

```bash
cp .env.example .env
```

Open `.env` and fill in at minimum:

```env
BOT_TOKEN=123456:AAA...           # from @BotFather
ADMIN_GROUP_ID=-1001234567890     # group where payment notifications go
ADMIN_TELEGRAM_IDS=123456789      # your Telegram user id
```

Optional: `CHANNEL_ID` + `CHANNEL_USERNAME` if you want to enforce channel subscription.

### 3. Initialize DB + demo data

```bash
python manage.py migrate
python manage.py seed_demo         # populates trainers, programs, cards, plans…
python manage.py createsuperuser   # for the admin panel
```

### 4. Run it (two terminals)

Terminal 1 — the admin panel:
```bash
python manage.py runserver
# → http://127.0.0.1:8000/admin/
```

Terminal 2 — the bot:
```bash
python manage.py runbot
# or equivalently:  python -m bot.main
```

Send `/start` to your bot in Telegram. Done. 🎉

---

## 🏗️ Project structure

```
gym-bot-project/
├── config/                   # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py / asgi.py
├── apps/                     # Django apps
│   ├── users/                #   TelegramUser, Language, Trainer + admin
│   ├── gym/                  #   GymProgram, MembershipPlan, Schedule,
│   │                         #   NutritionPlan, Discount, Testimonial
│   ├── enrollments/          #   Enrollment
│   └── payments/             #   Payment, PaymentCard, Refund, …
├── bot/
│   ├── main.py               # Bot entry point
│   ├── keyboards.py          # All inline keyboards
│   ├── states.py             # FSM state groups
│   ├── services.py           # Async Django ORM bridges
│   ├── middlewares.py        # Language injection + block check
│   ├── handlers/
│   │   ├── common.py         # /start, language, subscription, menu home
│   │   ├── info.py           # About, contact, membership, results, nutrition, …
│   │   ├── enrollment.py     # Program selection + screenshot upload
│   │   ├── ai.py             # AI fitness assistant
│   │   └── admin.py          # Admin-group approve/reject buttons
│   └── utils/
│       ├── i18n.py           # All multilingual texts
│       └── notifier.py       # Sync Telegram HTTP notifier (for signals)
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `BOT_TOKEN` | ✅ | — | Your bot token from @BotFather |
| `ADMIN_GROUP_ID` | ⚠️ | `0` | Group chat id that receives payment notifications |
| `ADMIN_TELEGRAM_IDS` | ⚠️ | — | Comma-separated admin user ids |
| `CHANNEL_ID` | — | — | `@channel` or `-100…` for subscription check |
| `CHANNEL_USERNAME` | — | — | Bare username for join link |
| `PAYMENT_PHONE` | — | `+998 90 000 00 00` | Shown on payment info screen |
| `PAYMENT_FULL_NAME` | — | `GYM ELITE` | Shown on payment info screen |
| `SECRET_KEY` | — | dev default | Django secret key |
| `DEBUG` | — | `True` | Django debug flag |
| `DB_ENGINE` | — | `sqlite` | Set to `postgres` for PostgreSQL |
| `DB_NAME/USER/PASSWORD/HOST/PORT` | — | — | Only if `DB_ENGINE=postgres` |
| `REDIS_URL` | — | — | If set, uses Redis FSM storage |
| `OPENAI_API_KEY` | — | — | If set, AI assistant uses GPT-4o-mini |

---

## 🔁 Payment flow, end-to-end

```
USER                               BOT / DJANGO                      ADMIN GROUP
────                               ────────────                      ───────────
📝 Join Program
→ pick program
→ see card details                 enroll:<id> → cards + rules
→ tap “Understood, sending”        pay_ok:<id> → ask for screenshot
→ sends photo                      POST creates Payment (pending)
                                     │
                                     │  Django post_save signal
                                     ▼
                                   notify_admin_new_payment()  ────▶  📸 Screenshot + info
                                                                       [✅ Approve] [❌ Reject]
                                                                              │
                                                                              │ (admin taps)
                                                                              ▼
                                   admin handler sets status='approved'
                                   notify_user_payment_approved()  ──▶  🎉 “Your payment is approved!”
                                   OR status='rejected'
                                   notify_user_payment_rejected()  ──▶  ❌ “Your payment was rejected”
```

Alternative: admin can also approve/reject via the web admin at `/admin/payments/payment/`.

---

## 🎨 Admin panel preview

- **Dark theme** via Jazzmin
- Colour-coded status pills (pending orange, approved green, rejected red)
- Payment card numbers auto-masked in list view
- Inline **Approve / Reject** buttons on each pending payment row
- Trainer avatars, program icons, progress bars on enrollments

---

## 🧪 Testing locally without a public Telegram group

1. Fill in `BOT_TOKEN`
2. Leave `CHANNEL_ID` empty → subscription check is bypassed
3. Set `ADMIN_TELEGRAM_IDS` to your own numeric Telegram id (find via @userinfobot)
4. Leave `ADMIN_GROUP_ID=0` — payments will still be created, just no group notification
5. Approve/reject from the Django admin — user will still get the Telegram DM

---

## 🛠️ Common tasks

```bash
# Add a new admin user
python manage.py createsuperuser

# Reset the database (dev only!)
rm db.sqlite3 && python manage.py migrate && python manage.py seed_demo

# Show all registered routes
python manage.py show_urls           # requires django-extensions (optional)

# Run with PostgreSQL instead of SQLite
# In .env:
#   DB_ENGINE=postgres
#   DB_NAME=gym_bot
#   DB_USER=...
pip install psycopg2-binary
python manage.py migrate
```

---

## 🩹 Troubleshooting

**“BOT_TOKEN is not set”** → Fill in `.env` and restart.

**Channel subscription check always fails** → The bot must be an **administrator** of
the channel. Add the bot as admin, then try again.

**Admin group doesn’t receive notifications** → Make sure the bot is in the group, and
`ADMIN_GROUP_ID` is the correct `-100…` numeric id (forward any message from the group
to @JsonDumpBot to get it).

**“relation does not exist”** errors → Run `python manage.py migrate`.

---

## 📄 License

MIT — feel free to use and modify.
