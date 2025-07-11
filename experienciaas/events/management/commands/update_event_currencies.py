from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
import random

from experienciaas.events.models import Event


class Command(BaseCommand):
    help = 'Update some events with different currencies for testing'

    def handle(self, *args, **options):
        # Get some events to update
        events = Event.objects.filter(price_type='paid')[:10]
        
        # Different currencies and prices for testing
        currency_data = [
            ('USD', [25.00, 35.00, 50.00, 75.00, 100.00]),
            ('EUR', [20.00, 30.00, 45.00, 65.00, 85.00]),
            ('COP', [80000, 120000, 150000, 200000, 300000]),
            ('GBP', [18.00, 25.00, 40.00, 55.00, 70.00]),
            ('CAD', [30.00, 45.00, 60.00, 85.00, 120.00]),
            ('MXN', [450, 650, 850, 1200, 1500]),
            ('BRL', [120, 180, 240, 320, 450]),
            ('ARS', [8500, 12000, 15000, 22000, 35000]),
        ]
        
        updated_count = 0
        
        for event in events:
            # Choose a random currency and price
            currency, prices = random.choice(currency_data)
            price = Decimal(str(random.choice(prices)))
            
            # Update the event
            event.currency = currency
            event.price = price
            event.save()
            
            updated_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Updated "{event.title}" - {currency} {price}'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated_count} events with different currencies'
            )
        )
