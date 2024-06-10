from django.core.management.base import BaseCommand
from users.models import User
import os

class Command(BaseCommand):
    help = 'Create a superuser with provided credentials'

    def handle(self, *args, **options):
        email = os.environ.get('SUPERUSER_EMAIL', 'admin@gh_bball.com')
        password = os.environ.get('SUPERUSER_PASSWORD', '!Qaz2wsx')

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(email, password)
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser already exists'))
