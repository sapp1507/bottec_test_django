from django.contrib.auth.models import User
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = """
    Заполняет БД данными
    """

    def add_arguments(self, parser):
        parser.add_argument('-s', '--superuser', action='store_true', help='Создать суперпользователя')

    def handle(self, *args, **options):
        ic('Start deploy')

        if options['superuser']:
            self.update_or_create_superuser()

    def update_or_create_superuser(self):
        ic('Update or create superuser')
        user, create = User.objects.update_or_create(
            id=1,
            defaults={
                'username': 'admin',
                'is_superuser': True,
                'is_staff': 'True'
            }
        )
        user.set_password('12wqasxz')
        user.save()