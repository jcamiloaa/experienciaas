from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class City(models.Model):
    """Model for cities where events can take place."""
    name = models.CharField(_("City name"), max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    country = models.CharField(_("Country"), max_length=100)
    is_active = models.BooleanField(_("Is active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
        ordering = ["name"]
    
    def __str__(self):
        return f"{self.name}, {self.country}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Category(models.Model):
    """Model for event categories."""
    name = models.CharField(_("Category name"), max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(_("Description"), blank=True)
    icon = models.CharField(_("Icon class"), max_length=50, blank=True, 
                           help_text=_("CSS icon class (e.g., fas fa-music)"))
    color = models.CharField(_("Color"), max_length=7, default="#3B82F6",
                           help_text=_("Hex color code"))
    is_active = models.BooleanField(_("Is active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["name"]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Event(models.Model):
    """Model for events."""
    PRICE_TYPE_CHOICES = [
        ('free', _('Free')),
        ('paid', _('Paid')),
        ('donation', _('Donation')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('cancelled', _('Cancelled')),
        ('sold_out', _('Sold Out')),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', _('US Dollar (USD)')),
        ('EUR', _('Euro (EUR)')),
        ('COP', _('Colombian Peso (COP)')),
        ('GBP', _('British Pound (GBP)')),
        ('CAD', _('Canadian Dollar (CAD)')),
        ('AUD', _('Australian Dollar (AUD)')),
        ('MXN', _('Mexican Peso (MXN)')),
        ('BRL', _('Brazilian Real (BRL)')),
        ('ARS', _('Argentine Peso (ARS)')),
        ('CLP', _('Chilean Peso (CLP)')),
        ('PEN', _('Peruvian Sol (PEN)')),
        ('UYU', _('Uruguayan Peso (UYU)')),
        ('JPY', _('Japanese Yen (JPY)')),
        ('CNY', _('Chinese Yuan (CNY)')),
        ('CHF', _('Swiss Franc (CHF)')),
        ('SEK', _('Swedish Krona (SEK)')),
        ('NOK', _('Norwegian Krone (NOK)')),
        ('DKK', _('Danish Krone (DKK)')),
    ]
    
    title = models.CharField(_("Event title"), max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(_("Description"))
    short_description = models.CharField(_("Short description"), max_length=300, blank=True)
    
    # Event details
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="events")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="events")
    
    # Date and time
    start_date = models.DateTimeField(_("Start date"))
    end_date = models.DateTimeField(_("End date"))
    
    # Location
    venue_name = models.CharField(_("Venue name"), max_length=200)
    address = models.TextField(_("Address"))
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Pricing
    price_type = models.CharField(max_length=10, choices=PRICE_TYPE_CHOICES, default='free')
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(_("Currency"), max_length=3, choices=CURRENCY_CHOICES, default="USD", blank=True)
    
    # Capacity
    max_attendees = models.PositiveIntegerField(_("Max attendees"), null=True, blank=True)
    
    # Sponsorship settings
    max_sponsors = models.PositiveIntegerField(_("Max sponsors"), default=0,
                                             help_text=_("Maximum number of sponsors for this event. Set to 0 to disable sponsorships."))
    sponsorship_open = models.BooleanField(_("Sponsorship applications open"), default=True,
                                         help_text=_("Allow new sponsorship applications"))
    
    # Media
    image = models.ImageField(_("Event image"), upload_to="events/images/", blank=True)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(_("Is featured"), default=False)
    views = models.PositiveIntegerField(_("Views"), default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["city", "start_date"]),
            models.Index(fields=["category", "start_date"]),
            models.Index(fields=["status", "start_date"]),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("events:detail", kwargs={"slug": self.slug})
    
    @property
    def is_free(self):
        return self.price_type == 'free'
    
    @property
    def is_sold_out(self):
        return self.status == 'sold_out'
    
    @property
    def attendees_count(self):
        return self.tickets.filter(status='confirmed').count()
    
    @property
    def remaining_tickets(self):
        if self.max_attendees:
            return max(0, self.max_attendees - self.attendees_count)
        return None

    @property
    def available_spots(self):
        """Alias for remaining_tickets to maintain consistency."""
        return self.remaining_tickets

    @property
    def duration(self):
        """Calculate and return the duration of the event."""
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            hours = delta.total_seconds() // 3600
            minutes = (delta.total_seconds() % 3600) // 60
            
            if hours >= 24:
                days = hours // 24
                remaining_hours = hours % 24
                if remaining_hours > 0:
                    return f"{int(days)} day(s), {int(remaining_hours)} hour(s)"
                else:
                    return f"{int(days)} day(s)"
            elif hours >= 1:
                if minutes > 0:
                    return f"{int(hours)} hour(s), {int(minutes)} minute(s)"
                else:
                    return f"{int(hours)} hour(s)"
            else:
                return f"{int(minutes)} minute(s)"
        return "N/A"

    @property
    def occupancy_rate(self):
        """Calculate the occupancy rate as a percentage."""
        if self.max_attendees and self.max_attendees > 0:
            return round((self.attendees_count / self.max_attendees) * 100, 1)
        return 0

    @property
    def sponsors_count(self):
        """Get the number of current sponsors."""
        return self.event_sponsors.count()

    @property
    def available_sponsor_slots(self):
        """Get the number of available sponsor slots."""
        if self.max_sponsors > 0:
            return max(0, self.max_sponsors - self.sponsors_count)
        return 0

    @property
    def sponsorship_available(self):
        """Check if sponsorship is available."""
        return (self.sponsorship_open and 
                self.max_sponsors > 0 and 
                self.sponsors_count < self.max_sponsors and
                self.status == 'published')

    @property
    def pending_applications_count(self):
        """Get the number of pending sponsorship applications."""
        return self.sponsorship_applications.filter(status='pending').count()

    def get_currency_symbol(self):
        """Get the currency symbol for display."""
        currency_symbols = {
            'USD': '$',
            'EUR': '€',
            'COP': '$',
            'GBP': '£',
            'CAD': 'C$',
            'AUD': 'A$',
            'MXN': '$',
            'BRL': 'R$',
            'ARS': '$',
            'CLP': '$',
            'PEN': 'S/',
            'UYU': '$U',
            'JPY': '¥',
            'CNY': '¥',
            'CHF': 'CHF',
            'SEK': 'kr',
            'NOK': 'kr',
            'DKK': 'kr'
        }
        return currency_symbols.get(self.currency, '$')

    def get_formatted_price(self):
        """Get the formatted price with currency symbol."""
        if self.price_type == 'free':
            return _('Free')
        elif self.price_type == 'donation':
            return _('Donation')
        elif self.price and self.price > 0:
            symbol = self.get_currency_symbol()
            return f"{symbol}{self.price:.2f}"
        return _('Free')

    @property
    def formatted_price(self):
        """Alias for get_formatted_price."""
        return self.get_formatted_price()


class Ticket(models.Model):
    """Model for event tickets/registrations."""
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('cancelled', _('Cancelled')),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tickets")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    
    # Ticket details
    ticket_number = models.CharField(_("Ticket number"), max_length=20, unique=True)
    attendee_name = models.CharField(_("Attendee name"), max_length=200)
    attendee_email = models.EmailField(_("Attendee email"))
    
    # Payment
    amount_paid = models.DecimalField(_("Amount paid"), max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(_("Payment method"), max_length=50, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")
        unique_together = [["event", "user"]]
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.ticket_number} - {self.event.title}"
    
    def save(self, *args, **kwargs):
        if not self.ticket_number:
            import uuid
            self.ticket_number = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)


class Sponsor(models.Model):
    """Model for event sponsors."""
    name = models.CharField(_("Company name"), max_length=200)
    logo = models.ImageField(_("Logo"), upload_to="sponsors/logos/", blank=True)
    description = models.TextField(_("Description"), max_length=500, blank=True)
    website = models.CharField(_("Website"), max_length=200, blank=True)
    contact_email = models.EmailField(_("Contact email"))
    contact_phone = models.CharField(_("Contact phone"), max_length=20, blank=True)
    
    # Social media
    facebook_url = models.URLField(_("Facebook URL"), blank=True)
    twitter_url = models.URLField(_("Twitter URL"), blank=True)
    instagram_url = models.URLField(_("Instagram URL"), blank=True)
    linkedin_url = models.URLField(_("LinkedIn URL"), blank=True)
    
    # Internal fields
    is_approved = models.BooleanField(_("Is approved"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Sponsor")
        verbose_name_plural = _("Sponsors")
        ordering = ["name"]
    
    def __str__(self):
        return self.name


class EventSponsor(models.Model):
    """Model for linking sponsors to events with sponsorship details."""
    TIER_CHOICES = [
        ('platinum', _('Platinum')),
        ('gold', _('Gold')),
        ('silver', _('Silver')),
        ('bronze', _('Bronze')),
        ('partner', _('Partner')),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="event_sponsors")
    sponsor = models.ForeignKey(Sponsor, on_delete=models.CASCADE, related_name="sponsored_events")
    tier = models.CharField(_("Sponsorship tier"), max_length=20, choices=TIER_CHOICES, default='partner')
    custom_description = models.TextField(_("Custom description"), max_length=300, blank=True,
                                        help_text=_("Override sponsor's default description for this event"))
    is_featured = models.BooleanField(_("Is featured"), default=False)
    display_order = models.PositiveIntegerField(_("Display order"), default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Event Sponsor")
        verbose_name_plural = _("Event Sponsors")
        unique_together = [["event", "sponsor"]]
        ordering = ["display_order", "tier", "sponsor__name"]
    
    def __str__(self):
        return f"{self.sponsor.name} - {self.event.title} ({self.get_tier_display()})"
    
    @property
    def description(self):
        """Get description (custom or default)."""
        return self.custom_description or self.sponsor.description


class SponsorshipApplication(models.Model):
    """Model for sponsorship applications."""
    STATUS_CHOICES = [
        ('pending', _('Pending Review')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('contacted', _('Contacted')),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="sponsorship_applications")
    
    # Company information
    company_name = models.CharField(_("Company name"), max_length=200)
    contact_name = models.CharField(_("Contact person name"), max_length=200)
    contact_email = models.EmailField(_("Contact email"))
    contact_phone = models.CharField(_("Contact phone"), max_length=20)
    company_website = models.CharField(_("Company website"), max_length=200, blank=True)
    
    # Sponsorship details
    message = models.TextField(_("Message"), max_length=1000,
                             help_text=_("Tell us about your company and why you want to sponsor this event"))
    proposed_tier = models.CharField(_("Proposed sponsorship tier"), max_length=20, 
                                   choices=EventSponsor.TIER_CHOICES, default='partner')
    
    # Status and processing
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(_("Admin notes"), blank=True, 
                                 help_text=_("Internal notes for organizers"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(_("Reviewed at"), null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name="reviewed_applications")
    
    class Meta:
        verbose_name = _("Sponsorship Application")
        verbose_name_plural = _("Sponsorship Applications")
        ordering = ["-created_at"]
        unique_together = [["event", "contact_email"]]  # One application per email per event
    
    def __str__(self):
        return f"{self.company_name} - {self.event.title} ({self.get_status_display()})"
