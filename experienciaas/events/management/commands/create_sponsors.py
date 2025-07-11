from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from experienciaas.events.models import Event, Sponsor, EventSponsor, SponsorshipApplication
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample sponsors and sponsorship data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of sponsors to create'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Sample sponsor data
        companies = [
            {
                'name': 'TechCorp Solutions',
                'description': 'Leading technology solutions provider specializing in enterprise software and cloud infrastructure.',
                'website': 'https://techcorp.example.com',
                'contact_email': 'partnerships@techcorp.example.com',
                'contact_phone': '+1-555-0101',
                'facebook_url': 'https://facebook.com/techcorp',
                'twitter_url': 'https://twitter.com/techcorp',
                'linkedin_url': 'https://linkedin.com/company/techcorp',
            },
            {
                'name': 'Digital Marketing Pro',
                'description': 'Full-service digital marketing agency helping businesses grow their online presence.',
                'website': 'https://digitalmarketingpro.example.com',
                'contact_email': 'hello@digitalmarketingpro.example.com',
                'contact_phone': '+1-555-0102',
                'instagram_url': 'https://instagram.com/digitalmarketingpro',
                'linkedin_url': 'https://linkedin.com/company/digitalmarketingpro',
            },
            {
                'name': 'GreenEnergy Co',
                'description': 'Sustainable energy solutions for a cleaner future. Solar, wind, and battery storage systems.',
                'website': 'https://greenenergy.example.com',
                'contact_email': 'sponsorships@greenenergy.example.com',
                'contact_phone': '+1-555-0103',
                'facebook_url': 'https://facebook.com/greenenergy',
                'twitter_url': 'https://twitter.com/greenenergy',
            },
            {
                'name': 'FinanceFirst Bank',
                'description': 'Community bank providing personal and business banking services with a focus on customer relationships.',
                'website': 'https://financefirst.example.com',
                'contact_email': 'marketing@financefirst.example.com',
                'contact_phone': '+1-555-0104',
                'linkedin_url': 'https://linkedin.com/company/financefirst',
            },
            {
                'name': 'FoodieDelight Catering',
                'description': 'Premium catering services for events, meetings, and special occasions. Fresh, local ingredients.',
                'website': 'https://foodiedelight.example.com',
                'contact_email': 'events@foodiedelight.example.com',
                'contact_phone': '+1-555-0105',
                'instagram_url': 'https://instagram.com/foodiedelight',
                'facebook_url': 'https://facebook.com/foodiedelight',
            },
            {
                'name': 'Creative Design Studio',
                'description': 'Award-winning design studio specializing in branding, web design, and marketing materials.',
                'website': 'https://creativedesign.example.com',
                'contact_email': 'partnerships@creativedesign.example.com',
                'contact_phone': '+1-555-0106',
                'instagram_url': 'https://instagram.com/creativedesign',
                'twitter_url': 'https://twitter.com/creativedesign',
                'linkedin_url': 'https://linkedin.com/company/creativedesign',
            },
            {
                'name': 'HealthPlus Wellness',
                'description': 'Comprehensive wellness solutions including fitness programs, nutrition consulting, and mental health support.',
                'website': 'https://healthplus.example.com',
                'contact_email': 'partnerships@healthplus.example.com',
                'contact_phone': '+1-555-0107',
                'facebook_url': 'https://facebook.com/healthplus',
                'instagram_url': 'https://instagram.com/healthplus',
            },
            {
                'name': 'CloudSecure IT',
                'description': 'Cybersecurity and cloud infrastructure services for small to medium businesses.',
                'website': 'https://cloudsecure.example.com',
                'contact_email': 'business@cloudsecure.example.com',
                'contact_phone': '+1-555-0108',
                'linkedin_url': 'https://linkedin.com/company/cloudsecure',
                'twitter_url': 'https://twitter.com/cloudsecure',
            },
            {
                'name': 'LocalBrew Coffee',
                'description': 'Artisan coffee roasters and café chain committed to fair trade and sustainable practices.',
                'website': 'https://localbrew.example.com',
                'contact_email': 'events@localbrew.example.com',
                'contact_phone': '+1-555-0109',
                'instagram_url': 'https://instagram.com/localbrew',
                'facebook_url': 'https://facebook.com/localbrew',
            },
            {
                'name': 'EduTech Learning',
                'description': 'Online learning platform and educational technology solutions for schools and organizations.',
                'website': 'https://edutech.example.com',
                'contact_email': 'partnerships@edutech.example.com',
                'contact_phone': '+1-555-0110',
                'linkedin_url': 'https://linkedin.com/company/edutech',
                'twitter_url': 'https://twitter.com/edutech',
            },
        ]
        
        created_sponsors = []
        
        # Create sponsors
        self.stdout.write(f"Creating {min(count, len(companies))} sponsors...")
        
        for i in range(min(count, len(companies))):
            company_data = companies[i]
            
            sponsor, created = Sponsor.objects.get_or_create(
                name=company_data['name'],
                defaults={
                    'description': company_data['description'],
                    'website': company_data['website'],
                    'contact_email': company_data['contact_email'],
                    'contact_phone': company_data['contact_phone'],
                    'facebook_url': company_data.get('facebook_url', ''),
                    'twitter_url': company_data.get('twitter_url', ''),
                    'instagram_url': company_data.get('instagram_url', ''),
                    'linkedin_url': company_data.get('linkedin_url', ''),
                    'is_approved': True,
                }
            )
            
            if created:
                created_sponsors.append(sponsor)
                self.stdout.write(f"  Created sponsor: {sponsor.name}")
            else:
                self.stdout.write(f"  Sponsor already exists: {sponsor.name}")
        
        # Get published events that support sponsorships
        events_with_sponsorships = Event.objects.filter(
            status='published',
            max_sponsors__gt=0
        )
        
        if not events_with_sponsorships.exists():
            # Update some events to support sponsorships
            events_to_update = Event.objects.filter(status='published')[:5]
            for event in events_to_update:
                event.max_sponsors = random.randint(3, 8)
                event.sponsorship_open = True
                event.save()
            events_with_sponsorships = events_to_update
            self.stdout.write(f"Updated {events_to_update.count()} events to support sponsorships")
        
        # Add some sponsors to events
        tiers = ['platinum', 'gold', 'silver', 'bronze', 'partner']
        sponsors = list(Sponsor.objects.all())
        
        for event in events_with_sponsorships[:3]:  # Add sponsors to first 3 events
            num_sponsors = min(random.randint(1, 3), len(sponsors), event.max_sponsors)
            event_sponsors = random.sample(sponsors, num_sponsors)
            
            for i, sponsor in enumerate(event_sponsors):
                event_sponsor, created = EventSponsor.objects.get_or_create(
                    event=event,
                    sponsor=sponsor,
                    defaults={
                        'tier': random.choice(tiers),
                        'display_order': i + 1,
                        'is_featured': i == 0,  # Make first sponsor featured
                    }
                )
                
                if created:
                    self.stdout.write(f"  Added {sponsor.name} as sponsor to {event.title}")
        
        # Create some sponsorship applications
        remaining_events = events_with_sponsorships[3:6]  # Use different events for applications
        remaining_sponsors = [s for s in sponsors if not EventSponsor.objects.filter(sponsor=s).exists()]
        
        for event in remaining_events:
            if remaining_sponsors:
                # Create 1-2 applications per event
                num_applications = min(random.randint(1, 2), len(remaining_sponsors))
                application_sponsors = random.sample(remaining_sponsors, num_applications)
                
                for sponsor in application_sponsors:
                    application, created = SponsorshipApplication.objects.get_or_create(
                        event=event,
                        contact_email=sponsor.contact_email,
                        defaults={
                            'company_name': sponsor.name,
                            'contact_name': f"Marketing Manager at {sponsor.name}",
                            'contact_email': sponsor.contact_email,
                            'contact_phone': sponsor.contact_phone,
                            'company_website': sponsor.website,
                            'message': f"We at {sponsor.name} are very interested in sponsoring {event.title}. "
                                     f"{sponsor.description[:200]}... We believe our partnership would be mutually beneficial "
                                     f"and help us reach our target audience while supporting this great event.",
                            'proposed_tier': random.choice(tiers),
                            'status': random.choice(['pending', 'pending', 'contacted']),  # Mostly pending
                        }
                    )
                    
                    if created:
                        self.stdout.write(f"  Created sponsorship application from {sponsor.name} for {event.title}")
                        remaining_sponsors.remove(sponsor)
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully created sponsorship data:\n"
                f"- {len(created_sponsors)} new sponsors\n"
                f"- {EventSponsor.objects.count()} event sponsorships\n"
                f"- {SponsorshipApplication.objects.count()} sponsorship applications"
            )
        )
