from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    # Organizer analytics
    path(
        "organizer/",
        views.organizer_analytics_view,
        name="organizer_dashboard"
    ),
    path(
        "organizer/api/",
        views.organizer_analytics_api,
        name="organizer_api"
    ),
    
    # Platform analytics (admin only)
    path(
        "platform/",
        views.platform_analytics_view,
        name="platform_dashboard"
    ),
    path(
        "platform/api/",
        views.platform_analytics_api,
        name="platform_api"
    ),
]
