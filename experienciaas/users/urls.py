from django.urls import path

from .views import (
    user_detail_view,
    user_redirect_view,
    user_update_view,
    organizer_profile_view,
    organizers_list_view,
    follow_organizer,
    profile_update_view,
)

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("~profile/", view=profile_update_view, name="profile_update"),
    path("organizers/", view=organizers_list_view, name="organizers_list"),
    path("organizer/<slug:slug>/", view=organizer_profile_view, name="organizer_profile"),
    path("organizer/<slug:slug>/follow/", view=follow_organizer, name="follow_organizer"),
    path("<int:pk>/", view=user_detail_view, name="detail"),
]
