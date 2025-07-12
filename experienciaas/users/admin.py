from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import User, OrganizerProfile, Follow, SupplierProfile, RoleApplication, SponsorshipApplication

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


@admin.register(RoleApplication)
class RoleApplicationAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "status", "created_at", "reviewed_by", "reviewed_at"]
    list_filter = ["role", "status", "created_at", "reviewed_at"]
    search_fields = ["user__name", "user__email", "motivation"]
    readonly_fields = ["created_at", "updated_at"]
    actions = ["approve_applications", "reject_applications", "mark_under_review"]
    
    fieldsets = (
        ("Application Info", {
            "fields": ("user", "role", "status")
        }),
        ("Details", {
            "fields": ("motivation", "experience", "additional_info")
        }),
        ("Review", {
            "fields": ("reviewed_by", "reviewed_at", "admin_notes", "rejection_reason"),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def approve_applications(self, request, queryset):
        """Approve selected role applications."""
        from django.utils import timezone
        approved = 0
        
        for application in queryset.filter(status='pending'):
            application.status = 'approved'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()
            
            # Create organizer profile if needed
            if application.role == 'organizer':
                application.user.is_staff = True
                application.user.save()
                if not hasattr(application.user, 'organizer_profile'):
                    OrganizerProfile.objects.create(user=application.user)
            
            approved += 1
        
        self.message_user(request, f"{approved} aplicaciones aprobadas.")
    approve_applications.short_description = "Aprobar aplicaciones seleccionadas"
    
    def reject_applications(self, request, queryset):
        """Reject selected role applications."""
        from django.utils import timezone
        rejected = 0
        
        for application in queryset.filter(status='pending'):
            application.status = 'rejected'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()
            rejected += 1
        
        self.message_user(request, f"{rejected} aplicaciones rechazadas.")
    reject_applications.short_description = "Rechazar aplicaciones seleccionadas"
    
    def mark_under_review(self, request, queryset):
        """Mark selected applications as under review."""
        updated = queryset.filter(status='pending').update(status='under_review')
        self.message_user(request, f"{updated} aplicaciones marcadas como en revisión.")
    mark_under_review.short_description = "Marcar como en revisión"


@admin.register(SupplierProfile)
class SupplierProfileAdmin(admin.ModelAdmin):
    list_display = ["company_name", "user", "status", "industry", "company_size", "is_approved", "created_at"]
    list_filter = ["status", "industry", "company_size", "is_public", "created_at", "approved_at"]
    search_fields = ["company_name", "user__name", "user__email", "company_description", "application_reason"]
    readonly_fields = ["slug", "created_at", "updated_at", "approved_at", "sponsored_events_count", "active_applications_count"]
    actions = ["approve_suppliers", "reject_suppliers", "suspend_suppliers"]
    
    fieldsets = (
        ("Basic Info", {
            "fields": ("user", "status", "slug")
        }),
        ("Company Information", {
            "fields": ("company_name", "company_description", "company_size", "industry", "founding_year")
        }),
        ("Legal Information", {
            "fields": ("tax_id", "legal_address"),
            "classes": ("collapse",)
        }),
        ("Contact Information", {
            "fields": ("business_phone", "business_email", "contact_person", "contact_position"),
            "classes": ("collapse",)
        }),
        ("Online Presence", {
            "fields": ("company_website", "facebook_url", "twitter_url", "instagram_url", "linkedin_url", "youtube_url"),
            "classes": ("collapse",)
        }),
        ("Marketing Materials", {
            "fields": ("company_logo", "company_banner", "brochure"),
            "classes": ("collapse",)
        }),
        ("Sponsorship Preferences", {
            "fields": ("sponsorship_budget_min", "sponsorship_budget_max", "preferred_event_types", "preferred_locations", "target_audience"),
            "classes": ("collapse",)
        }),
        ("Application", {
            "fields": ("application_reason",)
        }),
        ("Admin Review", {
            "fields": ("reviewed_by", "reviewed_at", "admin_notes", "rejection_reason"),
            "classes": ("collapse",)
        }),
        ("Settings", {
            "fields": ("is_public", "allow_contact", "email_notifications"),
            "classes": ("collapse",)
        }),
        ("Statistics", {
            "fields": ("sponsored_events_count", "active_applications_count"),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at", "approved_at"),
            "classes": ("collapse",)
        }),
    )
    
    def is_approved(self, obj):
        return obj.status == 'approved'
    is_approved.boolean = True
    is_approved.short_description = "Aprobado"
    
    def sponsored_events_count(self, obj):
        return obj.sponsored_events_count
    sponsored_events_count.short_description = "Eventos Patrocinados"
    
    def active_applications_count(self, obj):
        return obj.active_applications_count
    active_applications_count.short_description = "Aplicaciones Activas"
    
    def approve_suppliers(self, request, queryset):
        """Approve selected supplier profiles."""
        from django.utils import timezone
        approved = 0
        
        for supplier in queryset.filter(status='pending'):
            supplier.status = 'approved'
            supplier.reviewed_by = request.user
            supplier.reviewed_at = timezone.now()
            supplier.approved_at = timezone.now()
            supplier.save()
            approved += 1
        
        self.message_user(request, f"{approved} proveedores aprobados.")
    approve_suppliers.short_description = "Aprobar proveedores seleccionados"
    
    def reject_suppliers(self, request, queryset):
        """Reject selected supplier profiles."""
        from django.utils import timezone
        rejected = 0
        
        for supplier in queryset.filter(status='pending'):
            supplier.status = 'rejected'
            supplier.reviewed_by = request.user
            supplier.reviewed_at = timezone.now()
            supplier.save()
            rejected += 1
        
        self.message_user(request, f"{rejected} proveedores rechazados.")
    reject_suppliers.short_description = "Rechazar proveedores seleccionados"
    
    def suspend_suppliers(self, request, queryset):
        """Suspend selected supplier profiles."""
        from django.utils import timezone
        suspended = 0
        
        for supplier in queryset.filter(status='approved'):
            supplier.status = 'suspended'
            supplier.reviewed_by = request.user
            supplier.reviewed_at = timezone.now()
            supplier.save()
            suspended += 1
        
        self.message_user(request, f"{suspended} proveedores suspendidos.")
    suspend_suppliers.short_description = "Suspender proveedores seleccionados"


@admin.register(SponsorshipApplication)
class SponsorshipApplicationAdmin(admin.ModelAdmin):
    list_display = ["supplier_profile", "event", "proposed_tier", "budget_offered", "status", "created_at"]
    list_filter = ["status", "proposed_tier", "final_tier", "created_at", "reviewed_at"]
    search_fields = ["supplier_profile__company_name", "event__title", "message"]
    readonly_fields = ["created_at", "updated_at"]
    actions = ["approve_sponsorships", "reject_sponsorships", "mark_contracted"]
    
    fieldsets = (
        ("Application Info", {
            "fields": ("supplier_profile", "event", "status")
        }),
        ("Proposal", {
            "fields": ("proposed_tier", "budget_offered", "message", "special_requirements")
        }),
        ("Review", {
            "fields": ("reviewed_by", "reviewed_at", "organizer_notes", "admin_notes"),
            "classes": ("collapse",)
        }),
        ("Contract", {
            "fields": ("final_tier", "contract_amount", "contract_notes"),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def approve_sponsorships(self, request, queryset):
        """Approve selected sponsorship applications."""
        from django.utils import timezone
        approved = 0
        
        for application in queryset.filter(status='pending'):
            application.status = 'approved'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()
            approved += 1
        
        self.message_user(request, f"{approved} solicitudes de patrocinio aprobadas.")
    approve_sponsorships.short_description = "Aprobar solicitudes seleccionadas"
    
    def reject_sponsorships(self, request, queryset):
        """Reject selected sponsorship applications."""
        from django.utils import timezone
        rejected = 0
        
        for application in queryset.filter(status='pending'):
            application.status = 'rejected'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()
            rejected += 1
        
        self.message_user(request, f"{rejected} solicitudes de patrocinio rechazadas.")
    reject_sponsorships.short_description = "Rechazar solicitudes seleccionadas"
    
    def mark_contracted(self, request, queryset):
        """Mark selected applications as contracted."""
        updated = queryset.filter(status='approved').update(status='contracted')
        self.message_user(request, f"{updated} solicitudes marcadas como contratadas.")
    mark_contracted.short_description = "Marcar como contratadas"
