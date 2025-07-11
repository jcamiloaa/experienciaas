from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a staff user for testing admin functionality'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email for the staff user')
        parser.add_argument('--password', type=str, help='Password for the staff user')
        parser.add_argument('--name', type=str, help='Name for the staff user')

    def handle(self, *args, **options):
        email = options.get('email') or 'admin@experienciaas.com'
        password = options.get('password') or 'admin123'
        name = options.get('name') or 'Admin User'

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'User with email {email} already exists')
            )
            user = User.objects.get(email=email)
        else:
            user = User.objects.create_user(
                email=email,
                password=password,
                name=name
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created user: {email}')
            )

        # Make user staff and superuser
        user.is_staff = True
        user.is_superuser = True
        user.save()

        self.stdout.write(
            self.style.SUCCESS(f'User {email} is now staff and superuser')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Login credentials: {email} / {password}')
        )
