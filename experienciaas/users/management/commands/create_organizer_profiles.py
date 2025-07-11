from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from experienciaas.users.models import OrganizerProfile, Follow

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample organizer profiles and follows for testing'

    def handle(self, *args, **options):
        # Create some organizer profiles for existing staff users
        staff_users = User.objects.filter(is_staff=True)
        
        organizer_data = [
            {
                'bio': 'Especialista en eventos culturales y gastronómicos. Con más de 10 años de experiencia organizando festivales y experiencias únicas en la ciudad.',
                'location': 'Bogotá, Colombia',
                'website': 'https://eventosculturales.com',
                'phone': '+57 300 123 4567',
                'facebook_url': 'https://facebook.com/eventosculturales',
                'instagram_url': 'https://instagram.com/eventosculturales',
            },
            {
                'bio': 'Organizador de eventos deportivos y actividades al aire libre. Promovemos un estilo de vida activo y saludable a través de nuestros eventos.',
                'location': 'Medellín, Colombia',
                'website': 'https://deportesextremosmed.com',
                'phone': '+57 301 987 6543',
                'twitter_url': 'https://twitter.com/deportesmed',
                'instagram_url': 'https://instagram.com/deportesmed',
            },
            {
                'bio': 'Especialistas en conferencias tecnológicas y workshops de desarrollo. Conectamos a la comunidad tech de la ciudad.',
                'location': 'Cali, Colombia',
                'website': 'https://techcali.co',
                'linkedin_url': 'https://linkedin.com/company/techcali',
                'twitter_url': 'https://twitter.com/techcali',
            }
        ]
        
        created_profiles = 0
        
        for i, staff_user in enumerate(staff_users[:3]):  # Limit to first 3 staff users
            # Check if organizer profile already exists
            if hasattr(staff_user, 'organizer_profile'):
                profile = staff_user.organizer_profile
                self.stdout.write(f'Updating existing profile for {staff_user.email}')
            else:
                profile = OrganizerProfile.objects.create(user=staff_user)
                self.stdout.write(f'Created new profile for {staff_user.email}')
            
            # Update profile data if we have data for this index
            if i < len(organizer_data):
                data = organizer_data[i]
                for key, value in data.items():
                    setattr(profile, key, value)
                profile.save()
                created_profiles += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'Updated profile for {staff_user.email}')
                )
        
        # Create some follow relationships for testing
        profiles = OrganizerProfile.objects.filter(is_public=True)
        regular_users = User.objects.filter(is_staff=False, is_superuser=False)
        
        follow_count = 0
        
        for user in regular_users[:5]:  # Take first 5 regular users
            for profile in profiles:
                # Create some random follows (not all users follow all organizers)
                if follow_count % 3 == 0:  # Every 3rd combination
                    follow, created = Follow.objects.get_or_create(
                        follower=user,
                        organizer=profile
                    )
                    if created:
                        follow_count += 1
                        self.stdout.write(
                            f'{user.email} is now following {profile.user.email}'
                        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {created_profiles} organizer profiles and created {follow_count} follow relationships'
            )
        )
