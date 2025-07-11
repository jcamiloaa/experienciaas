from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class EventView(models.Model):
    """Track event page views for analytics."""
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='event_views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Event View")
        verbose_name_plural = _("Event Views")
        indexes = [
            models.Index(fields=['event', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]


class OrganizerView(models.Model):
    """Track organizer profile views for analytics."""
    organizer = models.ForeignKey('users.OrganizerProfile', on_delete=models.CASCADE, related_name='profile_views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Organizer View")
        verbose_name_plural = _("Organizer Views")
        indexes = [
            models.Index(fields=['organizer', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]


class SearchQuery(models.Model):
    """Track search queries for analytics and improvements."""
    query = models.CharField(_("Search query"), max_length=200)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    results_count = models.PositiveIntegerField(_("Results count"), default=0)
    category = models.ForeignKey('events.Category', on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey('events.City', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Search Query")
        verbose_name_plural = _("Search Queries")
        indexes = [
            models.Index(fields=['query']),
            models.Index(fields=['timestamp']),
        ]


class TicketRegistration(models.Model):
    """Track ticket registration funnel for analytics."""
    STEP_CHOICES = [
        ('started', _('Registration Started')),
        ('form_filled', _('Form Filled')),
        ('payment_attempted', _('Payment Attempted')),
        ('completed', _('Registration Completed')),
        ('abandoned', _('Registration Abandoned')),
    ]
    
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='registration_analytics')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(_("Session ID"), max_length=50)
    step = models.CharField(_("Registration step"), max_length=20, choices=STEP_CHOICES)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Ticket Registration Analytics")
        verbose_name_plural = _("Ticket Registration Analytics")
        indexes = [
            models.Index(fields=['event', 'step', 'timestamp']),
            models.Index(fields=['session_id']),
        ]


class DailyStats(models.Model):
    """Daily aggregated statistics for faster reporting."""
    date = models.DateField(_("Date"))
    
    # Event stats
    total_events = models.PositiveIntegerField(_("Total events"), default=0)
    new_events = models.PositiveIntegerField(_("New events"), default=0)
    published_events = models.PositiveIntegerField(_("Published events"), default=0)
    
    # User stats
    total_users = models.PositiveIntegerField(_("Total users"), default=0)
    new_users = models.PositiveIntegerField(_("New users"), default=0)
    active_users = models.PositiveIntegerField(_("Active users"), default=0)
    
    # Ticket stats
    total_tickets = models.PositiveIntegerField(_("Total tickets"), default=0)
    new_tickets = models.PositiveIntegerField(_("New tickets"), default=0)
    confirmed_tickets = models.PositiveIntegerField(_("Confirmed tickets"), default=0)
    
    # Revenue stats
    total_revenue = models.DecimalField(_("Total revenue"), max_digits=12, decimal_places=2, default=0)
    new_revenue = models.DecimalField(_("New revenue"), max_digits=12, decimal_places=2, default=0)
    
    # Traffic stats
    total_views = models.PositiveIntegerField(_("Total views"), default=0)
    unique_visitors = models.PositiveIntegerField(_("Unique visitors"), default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Daily Statistics")
        verbose_name_plural = _("Daily Statistics")
        unique_together = [('date',)]
        ordering = ['-date']


class OrganizerStats(models.Model):
    """Monthly organizer statistics for analytics dashboard."""
    organizer = models.ForeignKey('users.OrganizerProfile', on_delete=models.CASCADE, related_name='monthly_stats')
    year = models.PositiveIntegerField(_("Year"))
    month = models.PositiveIntegerField(_("Month"))
    
    # Event metrics
    events_created = models.PositiveIntegerField(_("Events created"), default=0)
    events_published = models.PositiveIntegerField(_("Events published"), default=0)
    total_attendees = models.PositiveIntegerField(_("Total attendees"), default=0)
    
    # Engagement metrics
    profile_views = models.PositiveIntegerField(_("Profile views"), default=0)
    event_views = models.PositiveIntegerField(_("Event views"), default=0)
    new_followers = models.PositiveIntegerField(_("New followers"), default=0)
    
    # Revenue metrics
    total_revenue = models.DecimalField(_("Total revenue"), max_digits=10, decimal_places=2, default=0)
    average_ticket_price = models.DecimalField(_("Average ticket price"), max_digits=8, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Organizer Statistics")
        verbose_name_plural = _("Organizer Statistics")
        unique_together = [('organizer', 'year', 'month')]
        ordering = ['-year', '-month']
