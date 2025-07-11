from django.urls import path

from . import views
from . import admin_views

app_name = "events"

urlpatterns = [
    path("", views.EventListView.as_view(), name="list"),
    path("my-events/", views.MyEventsView.as_view(), name="my_events"),
    path("city/<slug:city_slug>/", views.EventsByLocationView.as_view(), name="by_location"),
    path("category/<slug:category_slug>/", views.EventsByCategoryView.as_view(), name="by_category"),
    path("register/<slug:slug>/", views.RegisterForEventView.as_view(), name="register"),
    
    # Sponsorship URLs
    path("<slug:event_slug>/sponsor-apply/", views.SponsorshipApplicationCreateView.as_view(), name="sponsor_apply"),
    
    # Admin URLs
    path("admin/", admin_views.AdminDashboardView.as_view(), name="admin_dashboard"),
    path("admin/events/", admin_views.AdminEventListView.as_view(), name="admin_events"),
    path("admin/events/create/", admin_views.AdminEventCreateView.as_view(), name="admin_create_event"),
    path("admin/events/<int:pk>/", admin_views.AdminEventDetailView.as_view(), name="admin_event_detail"),
    path("admin/events/<int:pk>/edit/", admin_views.AdminEventUpdateView.as_view(), name="admin_edit_event"),
    path("admin/events/<int:pk>/delete/", admin_views.AdminEventDeleteView.as_view(), name="admin_delete_event"),
    path("admin/events/bulk-actions/", admin_views.AdminBulkActionView.as_view(), name="admin_bulk_actions"),
    path("admin/tickets/", admin_views.AdminTicketListView.as_view(), name="admin_tickets"),
    path("admin/tickets/<int:event_pk>/", admin_views.AdminTicketListView.as_view(), name="admin_event_tickets"),
    
    # Sponsor Management URLs
    path("admin/sponsors/", admin_views.AdminSponsorListView.as_view(), name="admin_sponsors"),
    path("admin/sponsors/create/", admin_views.AdminSponsorCreateView.as_view(), name="admin_create_sponsor"),
    path("admin/sponsors/<int:pk>/edit/", admin_views.AdminSponsorUpdateView.as_view(), name="admin_edit_sponsor"),
    path("admin/sponsors/<int:pk>/delete/", admin_views.AdminSponsorDeleteView.as_view(), name="admin_delete_sponsor"),
    
    # Event Sponsor Management URLs
    path("admin/events/<int:event_pk>/sponsors/add/", admin_views.AdminEventSponsorCreateView.as_view(), name="admin_add_event_sponsor"),
    path("admin/event-sponsors/<int:pk>/edit/", admin_views.AdminEventSponsorUpdateView.as_view(), name="admin_edit_event_sponsor"),
    path("admin/event-sponsors/<int:pk>/delete/", admin_views.AdminEventSponsorDeleteView.as_view(), name="admin_delete_event_sponsor"),
    
    # Sponsorship Application Management URLs
    path("admin/sponsorship-applications/", admin_views.AdminSponsorshipApplicationListView.as_view(), name="admin_sponsorship_applications"),
    path("admin/sponsorship-applications/<int:pk>/", admin_views.AdminSponsorshipApplicationDetailView.as_view(), name="admin_sponsorship_application_detail"),
    path("admin/sponsorship-applications/<int:pk>/edit/", admin_views.AdminSponsorshipApplicationUpdateView.as_view(), name="admin_edit_sponsorship_application"),
    path("admin/sponsorship-applications/<int:pk>/approve/", admin_views.AdminSponsorshipApplicationApproveView.as_view(), name="admin_approve_sponsorship_application"),
    path("admin/sponsorship-applications/<int:pk>/reject/", admin_views.AdminSponsorshipApplicationRejectView.as_view(), name="admin_reject_sponsorship_application"),
    
    # Public event detail (must be last to avoid conflicts)
    path("<slug:slug>/", views.EventDetailView.as_view(), name="detail"),
]
