from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum
from django.utils.translation import gettext_lazy as _

from .models import Category, City, Event, Ticket


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "country", "is_active", "events_count", "created_at"]
    list_filter = ["is_active", "country", "created_at"]
    search_fields = ["name", "country"]
    prepopulated_fields = {"slug": ("name",)}
    actions = ["make_active", "make_inactive"]
    
    def events_count(self, obj):
        count = obj.events.count()
        if count > 0:
            url = reverse("admin:events_event_changelist") + f"?city__id__exact={obj.id}"
            return format_html('<a href="{}">{} events</a>', url, count)
        return "0 events"
    events_count.short_description = "Events"
    
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} cities marked as active.")
    make_active.short_description = "Mark selected cities as active"
    
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} cities marked as inactive.")
    make_inactive.short_description = "Mark selected cities as inactive"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "color_preview", "icon_preview", "is_active", "events_count", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    actions = ["make_active", "make_inactive"]
    
    def color_preview(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 4px 8px; border-radius: 4px; color: white;">{}</span>',
            obj.color,
            obj.color
        )
    color_preview.short_description = "Color"
    
    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<i class="{}"></i> {}', obj.icon, obj.icon)
        return "-"
    icon_preview.short_description = "Icon"
    
    def events_count(self, obj):
        count = obj.events.count()
        if count > 0:
            url = reverse("admin:events_event_changelist") + f"?category__id__exact={obj.id}"
            return format_html('<a href="{}">{} events</a>', url, count)
        return "0 events"
    events_count.short_description = "Events"
    
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} categories marked as active.")
    make_active.short_description = "Mark selected categories as active"
    
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} categories marked as inactive.")
    make_inactive.short_description = "Mark selected categories as inactive"


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    readonly_fields = ["ticket_number", "created_at"]
    fields = ["ticket_number", "attendee_name", "attendee_email", "status", "amount_paid", "created_at"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        "title", "organizer", "city", "category", "start_date", 
        "price_display", "status", "attendees_count", "capacity_display", "views"
    ]
    list_filter = [
        "status", "price_type", "category", "city", "is_featured", 
        "start_date", "created_at"
    ]
    search_fields = ["title", "description", "venue_name", "organizer__name", "organizer__email"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "start_date"
    inlines = [TicketInline]
    actions = ["make_featured", "remove_featured", "publish_events", "draft_events"]
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("title", "slug", "description", "short_description", "organizer")
        }),
        ("Event Details", {
            "fields": ("category", "city", "venue_name", "address")
        }),
        ("Date & Time", {
            "fields": ("start_date", "end_date")
        }),
        ("Location", {
            "fields": ("latitude", "longitude"),
            "classes": ("collapse",)
        }),
        ("Pricing", {
            "fields": ("price_type", "price", "currency", "max_attendees")
        }),
        ("Media", {
            "fields": ("image",)
        }),
        ("Status & Features", {
            "fields": ("status", "is_featured", "views")
        }),
    )
    
    def price_display(self, obj):
        return obj.formatted_price
    price_display.short_description = "Price"
    
    def capacity_display(self, obj):
        if obj.max_attendees:
            attendees = obj.attendees_count
            return f"{attendees}/{obj.max_attendees}"
        return "Unlimited"
    capacity_display.short_description = "Capacity"
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} events marked as featured.")
    make_featured.short_description = "Mark selected events as featured"
    
    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"{updated} events removed from featured.")
    remove_featured.short_description = "Remove from featured"
    
    def publish_events(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f"{updated} events published.")
    publish_events.short_description = "Publish selected events"
    
    def draft_events(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f"{updated} events moved to draft.")
    draft_events.short_description = "Move to draft"


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        "ticket_number", "event", "attendee_name", "attendee_email", 
        "status", "amount_paid", "created_at"
    ]
    list_filter = ["status", "event__city", "event__category", "created_at"]
    search_fields = [
        "ticket_number", "attendee_name", "attendee_email", 
        "event__title", "user__name", "user__email"
    ]
    readonly_fields = ["ticket_number", "created_at", "updated_at"]
    actions = ["confirm_tickets", "cancel_tickets"]
    
    def confirm_tickets(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f"{updated} tickets confirmed.")
    confirm_tickets.short_description = "Confirm selected tickets"
    
    def cancel_tickets(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f"{updated} tickets cancelled.")
    cancel_tickets.short_description = "Cancel selected tickets"
