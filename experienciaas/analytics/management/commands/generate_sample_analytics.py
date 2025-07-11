from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random

from experienciaas.analytics.utils import generate_daily_stats
from experienciaas.analytics.models import EventView, OrganizerView, SearchQuery
from experienciaas.events.models import Event
from experienciaas.users.models import User, OrganizerProfile


class Command(BaseCommand):
    help = 'Generate sample analytics data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days of sample data to generate',
        )
        parser.add_argument(
            '--views',
            type=int,
            default=500,
            help='Number of sample views to generate',
        )

    def handle(self, *args, **options):
        days = options['days']
        views = options['views']
        
        self.stdout.write(f'Generating {views} sample analytics records for {days} days...')
        
        # Get sample data
        events = list(Event.objects.filter(status='published')[:20])
        users = list(User.objects.all()[:50])
        organizers = list(OrganizerProfile.objects.filter(is_public=True)[:10])
        
        if not events:
            self.stdout.write(
                self.style.ERROR('No published events found. Please create some events first.')
            )
            return
        
        # Generate sample IP addresses
        sample_ips = [
            '192.168.1.1', '10.0.0.1', '172.16.0.1', '203.0.113.1',
            '198.51.100.1', '192.0.2.1', '127.0.0.1', '192.168.0.1'
        ]
        
        # Generate sample user agents
        sample_user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)',
            'Mozilla/5.0 (Android 11; Mobile; rv:90.0) Gecko/90.0'
        ]
        
        # Generate event views
        event_views_created = 0
        for _ in range(views // 2):
            event = random.choice(events)
            user = random.choice(users) if random.random() > 0.3 else None
            timestamp = timezone.now() - timedelta(
                days=random.randint(0, days),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            EventView.objects.create(
                event=event,
                user=user,
                ip_address=random.choice(sample_ips),
                user_agent=random.choice(sample_user_agents),
                referrer='https://google.com' if random.random() > 0.5 else '',
                timestamp=timestamp
            )
            event_views_created += 1
        
        # Generate organizer views
        organizer_views_created = 0
        if organizers:
            for _ in range(views // 4):
                organizer = random.choice(organizers)
                user = random.choice(users) if random.random() > 0.3 else None
                timestamp = timezone.now() - timedelta(
                    days=random.randint(0, days),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                OrganizerView.objects.create(
                    organizer=organizer,
                    user=user,
                    ip_address=random.choice(sample_ips),
                    user_agent=random.choice(sample_user_agents),
                    referrer='https://google.com' if random.random() > 0.5 else '',
                    timestamp=timestamp
                )
                organizer_views_created += 1
        
        # Generate search queries
        sample_queries = [
            'concierto', 'música', 'arte', 'festival', 'teatro', 'danza',
            'comedia', 'conferencia', 'workshop', 'networking', 'tecnología',
            'emprendimiento', 'gastronomía', 'cine', 'fotografía', 'yoga',
            'fitness', 'educación', 'niños', 'familia', 'halloween', 'navidad'
        ]
        
        searches_created = 0
        for _ in range(views // 4):
            query = random.choice(sample_queries)
            user = random.choice(users) if random.random() > 0.4 else None
            timestamp = timezone.now() - timedelta(
                days=random.randint(0, days),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            SearchQuery.objects.create(
                query=query,
                user=user,
                ip_address=random.choice(sample_ips),
                results_count=random.randint(0, 50),
                timestamp=timestamp
            )
            searches_created += 1
        
        # Generate daily stats
        self.stdout.write('Generating daily statistics...')
        stats_created = 0
        for i in range(days):
            date = (timezone.now() - timedelta(days=i)).date()
            try:
                generate_daily_stats(date)
                stats_created += 1
            except Exception as e:
                self.stdout.write(f'Warning: Could not generate stats for {date}: {e}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated sample analytics data:\n'
                f'  - Event views: {event_views_created}\n'
                f'  - Organizer views: {organizer_views_created}\n'
                f'  - Search queries: {searches_created}\n'
                f'  - Daily stats: {stats_created} days'
            )
        )
