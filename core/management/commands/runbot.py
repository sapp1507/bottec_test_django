from django.core.management import BaseCommand

from bot.run import run_bot


class Command(BaseCommand):
    help = 'Запустить бота'

    def handle(self, *args, **options):
        run_bot()