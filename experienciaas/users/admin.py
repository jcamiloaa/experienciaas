from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import User, OrganizerProfile, Follow

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {
            "fields": ("name", "birth_date", "gender", "bio", "avatar")
        }),
        (_("Contact Information"), {
            "fields": ("country_code", "phone_number", "country", "city", "address", "postal_code")
        }),
        (_("Professional"), {
            "fields": ("occupation", "company", "website")
        }),
        (_("Social Media"), {
            "fields": ("linkedin_url", "twitter_url", "instagram_url", "facebook_url")
        }),
        (_("Interests"), {
            "fields": ("interests", "hobbies")
        }),
        (_("Privacy Settings"), {
            "fields": ("profile_visible", "show_email", "show_phone")
        }),
        (_("Notifications"), {
            "fields": ("email_notifications", "sms_notifications", "marketing_emails")
        }),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = [
        "email", "name", "age", "location", "occupation", "is_staff", "is_superuser", 
        "has_organizer_profile", "events_count", "followers_count", "date_joined"
    ]
    list_filter = [
        "is_staff", "is_superuser", "is_active", "date_joined", "gender", "country",
        "profile_visible", "email_notifications",
        ("organizer_profile", admin.EmptyFieldListFilter),
    ]
    search_fields = ["name", "email", "city", "occupation", "company"]
    readonly_fields = ["email", "date_joined", "last_login"]
    ordering = ["id"]
    
    def get_readonly_fields(self, request, obj=None):
        """Make email readonly for existing users, editable for new users."""
        if obj:  # Editing existing user
            return self.readonly_fields
        else:  # Creating new user
            return ["date_joined", "last_login"]
    actions = ["make_staff", "remove_staff", "create_organizer_profile", "toggle_organizer_public"]
    
    def age(self, obj):
        return obj.age or "-"
    age.short_description = _("Edad")
    
    def location(self, obj):
        return obj.location or "-"
    location.short_description = _("Ubicación")
    
    def has_organizer_profile(self, obj):
        if hasattr(obj, 'organizer_profile'):
            status = "Public" if obj.organizer_profile.is_public else "Private"
            return format_html(
                '<span class="badge badge-success">{}</span>', status
            )
        return format_html('<span class="badge badge-secondary">No</span>')
    has_organizer_profile.short_description = "Organizer Profile"
    
    def events_count(self, obj):
        if obj.is_staff:
            count = obj.organized_events.count()
            if count > 0:
                from django.urls import reverse
                url = reverse("admin:events_event_changelist") + f"?organizer__id__exact={obj.id}"
                return format_html('<a href="{}">{}</a>', url, count)
            return count
        return "-"
    events_count.short_description = "Events Created"
    
    def followers_count(self, obj):
        if hasattr(obj, 'organizer_profile'):
            return obj.organizer_profile.followers_count
        return "-"
    followers_count.short_description = "Followers"
    
    def make_staff(self, request, queryset):
        """Make selected users staff members and create organizer profiles."""
        updated = 0
        profiles_created = 0
        
        for user in queryset.filter(is_staff=False):
            user.is_staff = True
            user.save()
            updated += 1
            
            # Create organizer profile if it doesn't exist
            if not hasattr(user, 'organizer_profile'):
                from .models import OrganizerProfile
                OrganizerProfile.objects.create(user=user)
                profiles_created += 1
        
        message = f"{updated} users promoted to staff."
        if profiles_created > 0:
            message += f" {profiles_created} organizer profiles created."
        self.message_user(request, message)
    make_staff.short_description = "Promote to Staff & Create Organizer Profile"
    
    def remove_staff(self, request, queryset):
        """Remove staff status from selected users (except superusers)."""
        updated = queryset.filter(is_superuser=False).update(is_staff=False)
        self.message_user(request, f"{updated} users removed from staff.")
    remove_staff.short_description = "Remove Staff Status"
    
    def create_organizer_profile(self, request, queryset):
        """Create organizer profiles for selected staff users."""
        from .models import OrganizerProfile
        created = 0
        
        for user in queryset.filter(is_staff=True):
            if not hasattr(user, 'organizer_profile'):
                OrganizerProfile.objects.create(user=user)
                created += 1
        
        self.message_user(request, f"{created} organizer profiles created.")
    create_organizer_profile.short_description = "Create Organizer Profiles"
    
    def toggle_organizer_public(self, request, queryset):
        """Toggle public status of organizer profiles."""
        updated = 0
        for user in queryset:
            if hasattr(user, 'organizer_profile'):
                profile = user.organizer_profile
                profile.is_public = not profile.is_public
                profile.save()
                updated += 1
        
        self.message_user(request, f"{updated} organizer profiles toggled.")
    toggle_organizer_public.short_description = "Toggle Organizer Public Status"
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )


@admin.register(OrganizerProfile)
class OrganizerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "slug", "location", "is_public", "followers_count", "events_count", "created_at"]
    list_filter = ["is_public", "allow_contact", "created_at"]
    search_fields = ["user__name", "user__email", "bio", "location"]
    readonly_fields = ["slug", "followers_count", "events_count", "created_at", "updated_at"]
    
    fieldsets = (
        ("User", {"fields": ("user",)}),
        ("Profile Info", {"fields": ("bio", "location", "website", "phone")}),
        ("Social Media", {"fields": ("facebook_url", "twitter_url", "instagram_url", "linkedin_url")}),
        ("Images", {"fields": ("avatar", "cover_image")}),
        ("Settings", {"fields": ("is_public", "allow_contact")}),
        ("Statistics", {"fields": ("followers_count", "events_count"), "classes": ("collapse",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    
    def followers_count(self, obj):
        return obj.followers_count
    followers_count.short_description = "Followers"
    
    def events_count(self, obj):
        return obj.events_count
    events_count.short_description = "Events"


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ["follower", "organizer", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["follower__name", "follower__email", "organizer__user__name", "organizer__user__email"]
    readonly_fields = ["created_at"]
