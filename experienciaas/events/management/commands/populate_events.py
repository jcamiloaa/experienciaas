from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from experienciaas.events.models import City, Category, Event

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate the database with sample events data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))
        
        # Create cities
        cities_data = [
            {'name': 'Madrid', 'country': 'España'},
            {'name': 'Barcelona', 'country': 'España'},
            {'name': 'Valencia', 'country': 'España'},
            {'name': 'Sevilla', 'country': 'España'},
            {'name': 'Bogotá', 'country': 'Colombia'},
            {'name': 'Medellín', 'country': 'Colombia'},
            {'name': 'Cali', 'country': 'Colombia'},
            {'name': 'Buenos Aires', 'country': 'Argentina'},
            {'name': 'México DF', 'country': 'México'},
            {'name': 'Lima', 'country': 'Perú'},
        ]
        
        for city_data in cities_data:
            city, created = City.objects.get_or_create(
                name=city_data['name'],
                defaults={'country': city_data['country']}
            )
            if created:
                self.stdout.write(f'Created city: {city.name}')
        
        # Create categories
        categories_data = [
            {'name': 'Música', 'icon': 'fas fa-music', 'color': '#EF4444', 'description': 'Conciertos, festivales y eventos musicales'},
            {'name': 'Tecnología', 'icon': 'fas fa-laptop-code', 'color': '#3B82F6', 'description': 'Conferencias, workshops y meetups de tecnología'},
            {'name': 'Arte y Cultura', 'icon': 'fas fa-palette', 'color': '#8B5CF6', 'description': 'Exposiciones, teatro y eventos culturales'},
            {'name': 'Deportes', 'icon': 'fas fa-football-ball', 'color': '#10B981', 'description': 'Eventos deportivos y competiciones'},
            {'name': 'Gastronomía', 'icon': 'fas fa-utensils', 'color': '#F59E0B', 'description': 'Eventos gastronómicos y culinarios'},
            {'name': 'Educación', 'icon': 'fas fa-graduation-cap', 'color': '#6366F1', 'description': 'Cursos, talleres y seminarios educativos'},
            {'name': 'Negocios', 'icon': 'fas fa-briefcase', 'color': '#374151', 'description': 'Conferencias de negocios y networking'},
            {'name': 'Salud y Bienestar', 'icon': 'fas fa-heartbeat', 'color': '#EC4899', 'description': 'Eventos de salud, fitness y bienestar'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'icon': cat_data['icon'],
                    'color': cat_data['color'],
                    'description': cat_data['description']
                }
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create a sample organizer user
        organizer, created = User.objects.get_or_create(
            email='organizer@experienciaas.com',
            defaults={
                'name': 'Event Organizer',
                'is_active': True,
            }
        )
        if created:
            organizer.set_password('password123')
            organizer.save()
            self.stdout.write('Created organizer user')
        
        # Sample events data
        events_data = [
            {
                'title': 'Festival de Jazz Internacional',
                'description': 'Un festival de jazz que reúne a los mejores músicos internacionales en un ambiente único. Disfruta de tres días de música en vivo, con artistas de renombre mundial.',
                'short_description': 'Festival de jazz con artistas internacionales',
                'category': 'Música',
                'city': 'Madrid',
                'venue_name': 'Palacio de Deportes',
                'address': 'Av. Felipe II, s/n, 28009 Madrid',
                'price_type': 'paid',
                'price': 45.00,
                'max_attendees': 5000,
                'is_featured': True,
            },
            {
                'title': 'Conferencia de Inteligencia Artificial',
                'description': 'Una conferencia sobre las últimas tendencias en inteligencia artificial y machine learning. Expertos de la industria compartirán sus conocimientos.',
                'short_description': 'Conferencia sobre IA y ML',
                'category': 'Tecnología',
                'city': 'Barcelona',
                'venue_name': 'Centro de Convenciones',
                'address': 'Av. Diagonal, 661, 08028 Barcelona',
                'price_type': 'free',
                'max_attendees': 300,
                'is_featured': True,
            },
            {
                'title': 'Exposición de Arte Contemporáneo',
                'description': 'Una exposición que presenta obras de artistas contemporáneos locales e internacionales. Una oportunidad única para conocer las últimas tendencias artísticas.',
                'short_description': 'Exposición de arte contemporáneo',
                'category': 'Arte y Cultura',
                'city': 'Valencia',
                'venue_name': 'Museo de Arte Moderno',
                'address': 'Calle Guillem de Castro, 118, 46003 Valencia',
                'price_type': 'paid',
                'price': 12.00,
                'max_attendees': 200,
            },
            {
                'title': 'Torneo de Fútbol Amateur',
                'description': 'Torneo de fútbol para equipos amateur de la ciudad. Inscribe tu equipo y compite por el trofeo local.',
                'short_description': 'Torneo de fútbol amateur',
                'category': 'Deportes',
                'city': 'Sevilla',
                'venue_name': 'Estadio Municipal',
                'address': 'Av. del Deporte, 1, 41013 Sevilla',
                'price_type': 'free',
                'max_attendees': 1000,
            },
            {
                'title': 'Festival Gastronómico Internacional',
                'description': 'Un evento gastronómico que celebra la diversidad culinaria con chefs de diferentes países. Degustaciones, talleres y competencias.',
                'short_description': 'Festival gastronómico internacional',
                'category': 'Gastronomía',
                'city': 'Bogotá',
                'venue_name': 'Plaza de Bolívar',
                'address': 'Carrera 7 #11-10, Bogotá',
                'price_type': 'paid',
                'price': 25.00,
                'max_attendees': 800,
                'is_featured': True,
            },
            {
                'title': 'Workshop de Desarrollo Web',
                'description': 'Taller intensivo sobre desarrollo web moderno usando React, Node.js y bases de datos NoSQL. Incluye certificado de participación.',
                'short_description': 'Workshop de desarrollo web',
                'category': 'Tecnología',
                'city': 'Medellín',
                'venue_name': 'Centro de Innovación',
                'address': 'Carrera 46 #56-11, Medellín',
                'price_type': 'paid',
                'price': 80.00,
                'max_attendees': 50,
            },
            {
                'title': 'Concierto de Música Clásica',
                'description': 'Una noche de música clásica con la orquesta sinfónica nacional. Repertorio incluye obras de Mozart, Beethoven y Chopin.',
                'short_description': 'Concierto de música clásica',
                'category': 'Música',
                'city': 'Buenos Aires',
                'venue_name': 'Teatro Colón',
                'address': 'Cerrito 628, C1010 Buenos Aires',
                'price_type': 'paid',
                'price': 60.00,
                'max_attendees': 2000,
            },
            {
                'title': 'Seminario de Emprendimiento',
                'description': 'Seminario para emprendedores donde se abordan temas de financiamiento, marketing digital y estrategias de crecimiento.',
                'short_description': 'Seminario de emprendimiento',
                'category': 'Negocios',
                'city': 'México DF',
                'venue_name': 'World Trade Center',
                'address': 'Montecito #38, México DF',
                'price_type': 'free',
                'max_attendees': 400,
            },
            {
                'title': 'Maratón de la Ciudad',
                'description': 'Maratón anual que recorre los principales puntos turísticos de la ciudad. Incluye categorías de 5K, 10K y maratón completo.',
                'short_description': 'Maratón anual de la ciudad',
                'category': 'Deportes',
                'city': 'Lima',
                'venue_name': 'Malecón de Miraflores',
                'address': 'Malecón de la Reserva, Miraflores',
                'price_type': 'paid',
                'price': 35.00,
                'max_attendees': 3000,
            },
            {
                'title': 'Taller de Mindfulness y Meditación',
                'description': 'Aprende técnicas de mindfulness y meditación para reducir el estrés y mejorar tu bienestar mental.',
                'short_description': 'Taller de mindfulness',
                'category': 'Salud y Bienestar',
                'city': 'Cali',
                'venue_name': 'Centro de Bienestar',
                'address': 'Calle 5 #36-08, Cali',
                'price_type': 'paid',
                'price': 20.00,
                'max_attendees': 30,
            },
        ]
        
        # Create events
        for event_data in events_data:
            category = Category.objects.get(name=event_data['category'])
            city = City.objects.get(name=event_data['city'])
            
            # Random date in the next 60 days
            start_date = timezone.now() + timedelta(days=random.randint(1, 60))
            end_date = start_date + timedelta(hours=random.randint(2, 8))
            
            event, created = Event.objects.get_or_create(
                title=event_data['title'],
                defaults={
                    'description': event_data['description'],
                    'short_description': event_data['short_description'],
                    'organizer': organizer,
                    'category': category,
                    'city': city,
                    'venue_name': event_data['venue_name'],
                    'address': event_data['address'],
                    'start_date': start_date,
                    'end_date': end_date,
                    'price_type': event_data['price_type'],
                    'price': event_data.get('price'),
                    'max_attendees': event_data.get('max_attendees'),
                    'is_featured': event_data.get('is_featured', False),
                    'status': 'published',
                }
            )
            
            if created:
                self.stdout.write(f'Created event: {event.title}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated the database with sample data!')
        )
        self.stdout.write(
            self.style.WARNING('Remember to create a superuser to access the admin panel:')
        )
        self.stdout.write('python manage.py createsuperuser')
