from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from experienciaas.events.models import Event, Category, City

User = get_user_model()


class Command(BaseCommand):
    help = 'Create some donation-based events for testing'

    def handle(self, *args, **options):
        # Get or create a staff user
        try:
            organizer = User.objects.filter(is_staff=True).first()
            if not organizer:
                organizer = User.objects.create_user(
                    email="organizer@test.com",
                    password="testpass123",
                    name="Event Organizer",
                    is_staff=True
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating organizer: {e}')
            )
            return

        # Get categories and cities
        categories = list(Category.objects.filter(is_active=True))
        cities = list(City.objects.filter(is_active=True))
        
        if not categories or not cities:
            self.stdout.write(
                self.style.ERROR('No categories or cities found. Please create some first.')
            )
            return

        # Create donation events
        donation_events = [
            {
                'title': 'Concierto Benéfico para Educación',
                'short_description': 'Un hermoso concierto donde todos los fondos van para programas educativos locales.',
                'description': '''
                Únete a nosotros en una noche mágica de música en vivo donde cada donación contribuye directamente 
                a programas educativos para niños de bajos recursos. Contaremos con artistas locales y nacionales 
                que han donado su tiempo y talento para esta noble causa.
                
                - Músicos reconocidos
                - Rifas y premios
                - Refrigerios incluidos
                - Certificado de donación
                ''',
                'category': 'Música',
                'venue_name': 'Teatro Municipal',
                'address': 'Calle 15 #23-45, Centro'
            },
            {
                'title': 'Maratón Solidaria por el Medio Ambiente',
                'short_description': 'Corre por el planeta. Cada kilómetro cuenta para reforestar nuestra ciudad.',
                'description': '''
                Participa en nuestra maratón solidaria donde cada donación se destina a proyectos de reforestación 
                urbana. No importa si caminas, trotas o corres, lo importante es participar y contribuir.
                
                - Diferentes distancias: 5K, 10K, 21K
                - Kit del corredor incluido
                - Hidratación en ruta
                - Medalla conmemorativa
                - Certificado de participación
                ''',
                'category': 'Deportes',
                'venue_name': 'Parque Metropolitano',
                'address': 'Avenida 80 con Calle 53'
            },
            {
                'title': 'Festival de Arte por la Paz',
                'short_description': 'Expresiones artísticas que construyen paz. Tu donación apoya talleres comunitarios.',
                'description': '''
                Un festival donde el arte se convierte en el vehículo para promover la paz y la reconciliación. 
                Las donaciones recaudadas financiarán talleres de arte en comunidades vulnerables.
                
                - Exposiciones de arte visual
                - Performances en vivo
                - Talleres participativos
                - Música y danza
                - Actividades para toda la familia
                ''',
                'category': 'Arte y Cultura',
                'venue_name': 'Centro Cultural',
                'address': 'Carrera 7 #12-34, La Candelaria'
            }
        ]

        created_count = 0
        
        for event_data in donation_events:
            try:
                # Find category
                category = next((c for c in categories if event_data['category'].lower() in c.name.lower()), categories[0])
                city = cities[0]  # Use first city
                
                # Create the event
                event = Event.objects.create(
                    title=event_data['title'],
                    short_description=event_data['short_description'],
                    description=event_data['description'],
                    organizer=organizer,
                    category=category,
                    city=city,
                    start_date=timezone.now() + timedelta(days=30 + created_count * 7),
                    end_date=timezone.now() + timedelta(days=30 + created_count * 7, hours=4),
                    venue_name=event_data['venue_name'],
                    address=event_data['address'],
                    price_type='donation',
                    currency='COP',  # Use COP for donation events
                    max_attendees=500,
                    status='published',
                    is_featured=True
                )
                
                created_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'Created donation event: "{event.title}"')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating event "{event_data["title"]}": {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} donation events')
        )
