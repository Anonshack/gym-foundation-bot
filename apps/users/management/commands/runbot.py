"""
`python manage.py runbot` — convenience command to run the Telegram bot.
"""
import asyncio
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run the Telegram bot (polling mode).'

    def handle(self, *args, **options):
        from bot.main import main
        self.stdout.write(self.style.SUCCESS('🤖 Starting Telegram bot…'))
        try:
            asyncio.run(main())
        except (KeyboardInterrupt, SystemExit):
            self.stdout.write(self.style.WARNING('\n🛑 Bot stopped.'))
