"""
Test command to send Spanish emails
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model  
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

User = get_user_model()


class Command(BaseCommand):
    help = 'Envía correos de prueba en español'

    def handle(self, *args, **options):
        current_site = Site.objects.get_current()
        
        # Test 1: Correo de confirmación
        context = {
            'user': {'email': 'test@example.com', 'get_full_name': lambda: 'Usuario Test'},
            'current_site': current_site,
            'activate_url': f'http://{current_site.domain}/account/confirm-email/test-key/',
        }
        
        subject = render_to_string('account/email/email_confirmation_subject.txt', context).strip()
        message = render_to_string('account/email/email_confirmation_message.txt', context)
        
        try:
            send_mail(
                subject,
                message,
                f'noreply@{current_site.domain}',
                ['test@example.com'],
                fail_silently=False,
                html_message=render_to_string('account/email/email_confirmation_message.html', context)
            )
            self.stdout.write(
                self.style.SUCCESS('✓ Correo de confirmación enviado')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error enviando correo de confirmación: {e}')
            )
        
        # Test 2: Correo de reset de contraseña
        context = {
            'current_site': current_site,
            'password_reset_url': f'http://{current_site.domain}/account/password/reset/key/test-key/',
            'username': 'testuser',
        }
        
        subject = render_to_string('account/email/password_reset_key_subject.txt', context).strip()
        message = render_to_string('account/email/password_reset_key_message.txt', context)
        
        try:
            send_mail(
                subject,
                message,
                f'noreply@{current_site.domain}',
                ['test@example.com'],
                fail_silently=False,
                html_message=render_to_string('account/email/password_reset_key_message.html', context)
            )
            self.stdout.write(
                self.style.SUCCESS('✓ Correo de reset de contraseña enviado')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error enviando correo de reset: {e}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n¡Correos enviados! Revisa Mailpit en http://127.0.0.1:8025'
            )
        )
