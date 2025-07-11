from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum
from django.utils.translation import gettext_lazy as _

from .models import (
    EventView, OrganizerView, SearchQuery, TicketRegistration, 
    DailyStats, OrganizerStats
)


@admin.register(EventView)
class EventViewAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'ip_address', 'timestamp']
    list_filter = ['timestamp', 'event__category', 'event__city']
    search_fields = ['event__title', 'user__email', 'ip_address']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(OrganizerView)
class OrganizerViewAdmin(admin.ModelAdmin):
    list_display = ['organizer', 'user', 'ip_address', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['organizer__user__name', 'user__email', 'ip_address']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query', 'results_count', 'category', 'city', 'user', 'timestamp']
    list_filter = ['timestamp', 'category', 'city', 'results_count']
    search_fields = ['query', 'user__email']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(TicketRegistration)
class TicketRegistrationAdmin(admin.ModelAdmin):
    list_display = ['event', 'step', 'user', 'session_id', 'timestamp']
    list_filter = ['step', 'timestamp', 'event__category']
    search_fields = ['event__title', 'user__email', 'session_id']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'new_events', 'new_users', 'new_tickets', 
        'new_revenue_display', 'total_views', 'unique_visitors'
    ]
    list_filter = ['date']
    readonly_fields = [
        'total_events', 'new_events', 'published_events',
        'total_users', 'new_users', 'active_users',
        'total_tickets', 'new_tickets', 'confirmed_tickets',
        'total_revenue', 'new_revenue',
        'total_views', 'unique_visitors',
        'created_at', 'updated_at'
    ]
    date_hierarchy = 'date'
    
    def new_revenue_display(self, obj):
        return f"${obj.new_revenue:.2f}"
    new_revenue_display.short_description = "New Revenue"


@admin.register(OrganizerStats)
class OrganizerStatsAdmin(admin.ModelAdmin):
    list_display = [
        'organizer', 'year', 'month', 'events_created', 
        'total_attendees', 'profile_views', 'revenue_display'
    ]
    list_filter = ['year', 'month']
    search_fields = ['organizer__user__name', 'organizer__user__email']
    readonly_fields = [
        'events_created', 'events_published', 'total_attendees',
        'profile_views', 'event_views', 'new_followers',
        'total_revenue', 'average_ticket_price',
        'created_at', 'updated_at'
    ]
    
    def revenue_display(self, obj):
        return f"${obj.total_revenue:.2f}"
    revenue_display.short_description = "Revenue"


# Custom admin site for better organization
class AnalyticsAdminSite(admin.AdminSite):
    site_header = "Experienciaas Analytics"
    site_title = "Analytics Admin"
    index_title = "Platform Analytics Dashboard"


analytics_admin_site = AnalyticsAdminSite(name='analytics_admin')
