"""
Django settings for Gym CRM — clean, env-driven, works with SQLite by default.
Switch to PostgreSQL by setting DB_ENGINE=postgres + DB_* env vars.
"""
import os
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── CORE ────────────────────────────────────────────────────────────────────
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production-!!')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=Csv())

# ─── APPS ────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'jazzmin',                    # must be before django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Project apps
    'apps.users',
    'apps.gym',
    'apps.enrollments',
    'apps.payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ─── DATABASE ────────────────────────────────────────────────────────────────
# Accepts: 'sqlite' (default), 'postgres', 'postgresql', or a full Django ENGINE string.
DB_ENGINE_RAW = config('DB_ENGINE', default='sqlite').strip().lower()

_is_postgres = (
    DB_ENGINE_RAW in ('postgres', 'postgresql')
    or 'postgres' in DB_ENGINE_RAW
)

if _is_postgres:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='gym_bot'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default='postgres'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ─── AUTH ────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── I18N / TZ ───────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = config('TIME_ZONE', default='Asia/Tashkent')
USE_I18N = True
USE_TZ = True

# ─── STATIC / MEDIA ──────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── TELEGRAM BOT CONFIG ─────────────────────────────────────────────────────
BOT_TOKEN = config('BOT_TOKEN', default='')
CHANNEL_ID = config('CHANNEL_ID', default='')                   # e.g. @yourchannel or -1001234567890
CHANNEL_USERNAME = config('CHANNEL_USERNAME', default='')       # e.g. yourchannel (no @)
ADMIN_GROUP_ID = config('ADMIN_GROUP_ID', default='0')
ADMIN_TELEGRAM_IDS = config('ADMIN_TELEGRAM_IDS', default='', cast=Csv())

PAYMENT_PHONE = config('PAYMENT_PHONE', default='+998 90 000 00 00')
PAYMENT_FULL_NAME = config('PAYMENT_FULL_NAME', default='GYM ELITE')

# Optional Redis for FSM storage (falls back to memory if empty)
REDIS_URL = config('REDIS_URL', default='')

# ─── LOGGING ─────────────────────────────────────────────────────────────────
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
os.makedirs(MEDIA_ROOT, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname:<8} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'app.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {'handlers': ['console', 'file'], 'level': 'INFO'},
    'loggers': {
        'django': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': False},
        'bot':    {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': False},
        'apps':   {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': False},
    },
}

# ─── JAZZMIN ADMIN THEME ─────────────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    'site_title': 'Gym Elite CRM',
    'site_header': 'Gym Elite',
    'site_brand': '🏋️ Gym Elite',
    'welcome_sign': 'Welcome to Gym Elite Admin Panel',
    'copyright': 'Gym Elite',
    'user_avatar': None,

    'topmenu_links': [
        {'name': 'Home', 'url': 'admin:index', 'permissions': ['auth.view_user']},
        {'model': 'auth.User'},
        {'app': 'payments'},
    ],

    'icons': {
        'auth': 'fas fa-users-cog',
        'auth.user': 'fas fa-user',
        'auth.Group': 'fas fa-users',
        'users.TelegramUser': 'fas fa-user-circle',
        'users.Language': 'fas fa-language',
        'users.Trainer': 'fas fa-user-graduate',
        'gym.GymProgram': 'fas fa-dumbbell',
        'gym.MembershipPlan': 'fas fa-crown',
        'gym.Schedule': 'fas fa-calendar-alt',
        'gym.NutritionPlan': 'fas fa-apple-alt',
        'gym.Discount': 'fas fa-tag',
        'gym.Testimonial': 'fas fa-star',
        'enrollments.Enrollment': 'fas fa-clipboard-list',
        'payments.Payment': 'fas fa-money-bill-wave',
        'payments.PaymentCard': 'fas fa-credit-card',
        'payments.PaymentMethod': 'fas fa-cash-register',
        'payments.Refund': 'fas fa-undo',
        'payments.PaymentSettings': 'fas fa-cogs',
    },
    'default_icon_parents': 'fas fa-chevron-circle-right',
    'default_icon_children': 'fas fa-circle',
    'related_modal_active': True,
    'show_ui_builder': False,
    'order_with_respect_to': ['users', 'gym', 'enrollments', 'payments', 'auth'],
}

JAZZMIN_UI_TWEAKS = {
    'navbar_small_text': False,
    'footer_small_text': False,
    'body_small_text': False,
    'brand_small_text': False,
    'brand_colour': 'navbar-danger',
    'accent': 'accent-danger',
    'navbar': 'navbar-dark',
    'no_navbar_border': False,
    'navbar_fixed': True,
    'sidebar_fixed': True,
    'sidebar': 'sidebar-dark-danger',
    'sidebar_nav_flat_style': True,
    'theme': 'darkly',
    'dark_mode_theme': 'darkly',
    'button_classes': {
        'primary': 'btn-primary',
        'secondary': 'btn-secondary',
        'info': 'btn-info',
        'warning': 'btn-warning',
        'danger': 'btn-danger',
        'success': 'btn-success',
    },
}
