"""
Script para probar el envío de correos en español
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from allauth.account.models import EmailConfirmation, EmailAddress
from allauth.account.utils import send_email_confirmation
from django.conf import settings

User = get_user_model()


class Command(BaseCommand):
    help = 'Prueba el envío de correos en español'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email donde enviar la prueba')

    def handle(self, *args, **options):
        email = options['email']
        
        # Crear o obtener usuario de prueba
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'name': 'Usuario de Prueba',
                'is_active': False
            }
        )
        
        if created:
            self.stdout.write(f'Usuario creado: {user.email}')
        else:
            self.stdout.write(f'Usuario existente: {user.email}')
        
        # Enviar correo de confirmación
        try:
            send_email_confirmation(None, user, signup=True)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Correo de confirmación enviado a {email}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error enviando correo: {e}')
            )
