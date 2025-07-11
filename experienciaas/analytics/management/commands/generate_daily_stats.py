from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta

from experienciaas.analytics.utils import generate_daily_stats


class Command(BaseCommand):
    help = 'Generate daily statistics for analytics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date in YYYY-MM-DD format (default: yesterday)',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Number of days to generate stats for (working backwards from date)',
        )

    def handle(self, *args, **options):
        if options['date']:
            try:
                end_date = datetime.strptime(options['date'], '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('Invalid date format. Use YYYY-MM-DD.')
                )
                return
        else:
            # Default to yesterday
            end_date = (timezone.now() - timedelta(days=1)).date()

        days = options['days']
        
        self.stdout.write(f'Generating daily stats for {days} day(s) ending {end_date}...')
        
        for i in range(days):
            date = end_date - timedelta(days=i)
            
            try:
                stats = generate_daily_stats(date)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Generated stats for {date}: '
                        f'{stats.new_events} events, '
                        f'{stats.new_users} users, '
                        f'{stats.new_tickets} tickets, '
                        f'${stats.new_revenue:.2f} revenue'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to generate stats for {date}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Completed generating daily stats for {days} day(s).')
        )
