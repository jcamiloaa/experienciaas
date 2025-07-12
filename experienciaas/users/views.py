from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic import RedirectView
from django.views.generic import UpdateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

from .forms import SupplierProfileUpdateForm

from experienciaas.users.models import User, OrganizerProfile, Follow, RoleApplication, SupplierProfile
from experienciaas.users.forms import UserUpdateForm


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    success_message = _("Información actualizada exitosamente")

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None=None) -> User:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self) -> str:
        return reverse("events:list")


user_redirect_view = UserRedirectView.as_view()


class OrganizerProfileView(DetailView):
    """Public view for organizer profiles."""
    model = OrganizerProfile
    template_name = "users/organizer_profile.html"
    context_object_name = "organizer"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return OrganizerProfile.objects.filter(is_public=True).select_related('user')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        # Track analytics
        try:
            from experienciaas.analytics.utils import track_organizer_view
            track_organizer_view(obj, self.request)
        except ImportError:
            pass
        
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organizer = self.object
        
        # Get events with pagination
        event_type = self.request.GET.get('type', 'upcoming')
        
        if event_type == 'past':
            events = organizer.user.organized_events.filter(
                status__in=['published', 'sold_out'],
                start_date__lt=timezone.now()
            ).order_by('-start_date')
        else:
            events = organizer.user.organized_events.filter(
                status__in=['published', 'sold_out'],
                start_date__gte=timezone.now()
            ).order_by('start_date')
        
        # Pagination
        paginator = Paginator(events, 12)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context.update({
            'events': page_obj,
            'event_type': event_type,
            'upcoming_count': organizer.upcoming_events_count,
            'past_count': organizer.past_events_count,
            'is_following': False,
        })
        
        # Check if current user is following this organizer
        if self.request.user.is_authenticated:
            context['is_following'] = Follow.objects.filter(
                follower=self.request.user,
                organizer=organizer
            ).exists()
        
        return context


organizer_profile_view = OrganizerProfileView.as_view()


class OrganizersListView(ListView):
    """List view for all public organizers."""
    model = OrganizerProfile
    template_name = "users/organizers_list.html"
    context_object_name = "organizers"
    paginate_by = 24

    def get_queryset(self):
        queryset = OrganizerProfile.objects.filter(
            is_public=True
        ).select_related('user').order_by('-created_at')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                user__name__icontains=search
            ) | queryset.filter(
                bio__icontains=search
            ) | queryset.filter(
                location__icontains=search
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


organizers_list_view = OrganizersListView.as_view()


@login_required
@require_POST 
@csrf_protect
def follow_organizer(request, slug):
    """Follow/unfollow an organizer."""
    organizer = get_object_or_404(OrganizerProfile, slug=slug, is_public=True)
    
    # Prevent self-following
    if organizer.user == request.user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'No puedes seguirte a ti mismo.'
            })
        messages.error(request, _("You cannot follow yourself."))
        return redirect('users:organizer_profile', slug=slug)
    
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        organizer=organizer
    )
    
    if created:
        action = 'followed'
        message = _("You are now following {}.").format(
            organizer.user.name or organizer.user.email
        )
    else:
        follow.delete()
        action = 'unfollowed'
        message = _("You unfollowed {}.").format(
            organizer.user.name or organizer.user.email
        )
    
    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'action': action,
            'followers_count': organizer.followers_count,
            'is_following': action == 'followed',
            'message': str(message)
        })
    
    messages.success(request, message)
    return redirect('users:organizer_profile', slug=slug)


class UserProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Update organizer profile for staff users."""
    model = OrganizerProfile
    template_name = "users/profile_update.html"
    fields = [
        'bio', 'website', 'phone', 'location',
        'facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url',
        'avatar', 'cover_image', 'is_public', 'allow_contact'
    ]
    success_message = _("Profile successfully updated")
    
    def get_object(self):
        # Get or create organizer profile for the current user
        if not self.request.user.is_staff:
            messages.error(self.request, _("Only staff members can have organizer profiles."))
            return redirect('users:detail', pk=self.request.user.pk)
        
        profile, created = OrganizerProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile
    
    def get_success_url(self):
        return self.object.get_absolute_url()


profile_update_view = UserProfileUpdateView.as_view()


class SupplierProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Update supplier profile for users with approved supplier role."""
    model = SupplierProfile
    form_class = SupplierProfileUpdateForm
    template_name = "users/supplier_profile_update.html"
    success_message = _("Perfil de proveedor actualizado exitosamente")
    
    def get_object(self):
        # Check if user has approved supplier role
        if not self.request.user.is_supplier:
            messages.error(self.request, _("Solo los proveedores aprobados pueden acceder a esta página."))
            return redirect('users:detail', pk=self.request.user.pk)
        
        # Get the supplier profile
        try:
            profile = SupplierProfile.objects.get(user=self.request.user)
            if profile.status != 'approved':
                messages.error(self.request, _("Tu perfil de proveedor debe estar aprobado para editarlo."))
                return redirect('users:detail', pk=self.request.user.pk)
            return profile
        except SupplierProfile.DoesNotExist:
            messages.error(self.request, _("No tienes un perfil de proveedor."))
            return redirect('users:detail', pk=self.request.user.pk)
    
    def get_success_url(self):
        return reverse('users:detail', kwargs={'pk': self.request.user.pk})


supplier_profile_update_view = SupplierProfileUpdateView.as_view()


class AdminSupplierProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Admin view to edit any supplier profile."""
    model = SupplierProfile
    form_class = SupplierProfileUpdateForm
    template_name = "users/admin_supplier_profile_update.html"
    success_message = _("Perfil de proveedor actualizado exitosamente")
    pk_url_kwarg = 'profile_id'
    
    def dispatch(self, request, *args, **kwargs):
        # Only superusers can access this view
        if not request.user.is_superuser:
            messages.error(request, _("Solo los administradores principales pueden acceder a esta página."))
            return redirect('events:list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin_edit'] = True
        context['supplier_user'] = self.object.user
        return context
    
    def get_success_url(self):
        return reverse('events:admin_sponsors')


admin_edit_supplier_profile_view = AdminSupplierProfileUpdateView.as_view()


# Admin views for role management
@method_decorator(staff_member_required, name='dispatch')
class AdminRoleApplicationsView(ListView):
    """Admin view to manage role applications."""
    model = RoleApplication
    template_name = "users/admin_role_applications.html"
    context_object_name = "applications"
    paginate_by = 20
    
    def get_queryset(self):
        # Only superusers can see all applications
        if not self.request.user.is_superuser:
            messages.error(self.request, _("Access denied. Superuser permission required."))
            return RoleApplication.objects.none()
        
        queryset = RoleApplication.objects.select_related('user').order_by('-created_at')
        status = self.request.GET.get('status')
        role = self.request.GET.get('role')
        
        if status:
            queryset = queryset.filter(status=status)
        if role:
            queryset = queryset.filter(role=role)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = RoleApplication.STATUS_CHOICES
        context['role_choices'] = RoleApplication.ROLE_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        context['current_role'] = self.request.GET.get('role', '')
        return context


@method_decorator(staff_member_required, name='dispatch')
class AdminSupplierProfilesView(ListView):
    """Admin view to manage supplier profiles."""
    model = SupplierProfile
    template_name = "users/admin_supplier_profiles.html"
    context_object_name = "profiles"
    paginate_by = 20
    
    def get_queryset(self):
        # Only superusers can see all profiles
        if not self.request.user.is_superuser:
            messages.error(self.request, _("Access denied. Superuser permission required."))
            return SupplierProfile.objects.none()
        
        queryset = SupplierProfile.objects.select_related('user').order_by('-created_at')
        status = self.request.GET.get('status')
        
        if status:
            if status == 'approved':
                queryset = queryset.filter(is_approved=True)
            elif status == 'pending':
                queryset = queryset.filter(is_approved=False)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', '')
        return context


@require_POST
@staff_member_required
def approve_role_application(request, application_id):
    """Approve a role application."""
    if not request.user.is_superuser:
        messages.error(request, _("Access denied. Superuser permission required."))
        return redirect('users:admin_role_applications')
    
    application = get_object_or_404(RoleApplication, id=application_id)
    
    if application.status != 'pending':
        messages.warning(request, _("This application has already been processed."))
        return redirect('users:admin_role_applications')
    
    # Check if there's already an approved application for the same user and role
    existing_approved = RoleApplication.objects.filter(
        user=application.user,
        role=application.role,
        status='approved'
    ).exclude(id=application.id).first()
    
    if existing_approved:
        # Store information before deleting the application
        user = application.user
        role = application.role
        motivation = application.motivation
        
        # Delete the duplicate application instead of trying to set status to rejected
        application.delete()
        
        # Restore the role directly instead of creating duplicate application
        if role == 'organizer':
            user.is_staff = True
            # Clear any suspensions
            user.organizer_suspended = False
            user.organizer_suspended_by = None
            user.organizer_suspended_at = None
            user.organizer_suspended_until = None
            user.organizer_suspension_reason = ''
            user.save()
            
            # Create organizer profile if it doesn't exist
            OrganizerProfile.objects.get_or_create(user=user)
            messages.success(request, _(f"Role restored. {user.get_full_name()} is now an active organizer again."))
            
        elif role == 'supplier':
            # For suppliers, create or reactivate their profile
            supplier_profile, created = SupplierProfile.objects.get_or_create(
                user=user,
                defaults={
                    'company_name': user.get_full_name() or user.email,
                    'status': 'approved',
                    'approved_at': timezone.now(),
                    'application_reason': motivation,
                }
            )
            
            # If profile already exists, reactivate it
            if not created:
                supplier_profile.status = 'approved'
                supplier_profile.approved_at = timezone.now()
                supplier_profile.save()
                
            # Clear any suspensions
            user.supplier_suspended = False
            user.supplier_suspended_by = None
            user.supplier_suspended_at = None
            user.supplier_suspended_until = None
            user.supplier_suspension_reason = ''
            user.save()
            
            messages.success(request, _(f"Supplier role restored for {user.get_full_name()}."))
        
        return redirect('users:admin_role_applications')
    
    # If no existing approved application, proceed normally
    application.status = 'approved'
    application.processed_at = timezone.now()
    application.processed_by = request.user
    application.save()
    
    # Apply the role to the user
    user = application.user
    if application.role == 'organizer':
        user.is_staff = True
        # Clear any suspensions
        user.organizer_suspended = False
        user.organizer_suspended_by = None
        user.organizer_suspended_at = None
        user.organizer_suspended_until = None
        user.organizer_suspension_reason = ''
        user.save()
        
        # Create organizer profile if it doesn't exist
        OrganizerProfile.objects.get_or_create(user=user)
        messages.success(request, _(f"Role application approved. {user.get_full_name()} is now an organizer."))
        
    elif application.role == 'supplier':
        # For suppliers, create or update supplier profile
        supplier_profile, created = SupplierProfile.objects.get_or_create(
            user=user,
            defaults={
                'company_name': user.get_full_name() or user.email,
                'status': 'approved',
                'approved_at': timezone.now(),
                'application_reason': application.motivation,
            }
        )
        
        # If profile already exists, approve it
        if not created:
            supplier_profile.status = 'approved'
            supplier_profile.approved_at = timezone.now()
            supplier_profile.save()
        
        # Clear any suspensions
        user.supplier_suspended = False
        user.supplier_suspended_by = None
        user.supplier_suspended_at = None
        user.supplier_suspended_until = None
        user.supplier_suspension_reason = ''
        user.save()
        
        messages.success(request, _(f"Supplier application approved for {user.get_full_name()}. Supplier profile created/activated."))
    
    return redirect('users:admin_role_applications')


@require_POST
@staff_member_required
def reject_role_application(request, application_id):
    """Reject a role application."""
    if not request.user.is_superuser:
        messages.error(request, _("Access denied. Superuser permission required."))
        return redirect('users:admin_role_applications')
    
    application = get_object_or_404(RoleApplication, id=application_id)
    
    if application.status != 'pending':
        messages.warning(request, _("This application has already been processed."))
        return redirect('users:admin_role_applications')
    
    # Reject the application
    application.status = 'rejected'
    application.processed_at = timezone.now()
    application.processed_by = request.user
    application.save()
    
    messages.success(request, _(f"Role application rejected for {application.user.get_full_name()}."))
    return redirect('users:admin_role_applications')


@require_POST
@staff_member_required
def approve_supplier_profile(request, profile_id):
    """Approve a supplier profile."""
    if not request.user.is_superuser:
        messages.error(request, _("Access denied. Superuser permission required."))
        return redirect('users:admin_supplier_profiles')
    
    profile = get_object_or_404(SupplierProfile, id=profile_id)
    
    if profile.status == 'approved':
        messages.warning(request, _("This supplier profile is already approved."))
        return redirect('users:admin_supplier_profiles')
    
    profile.status = 'approved'
    profile.approved_at = timezone.now()
    profile.save()
    
    messages.success(request, _(f"Supplier profile approved for {profile.user.get_full_name()}."))
    return redirect('users:admin_supplier_profiles')


@require_POST
@staff_member_required
def reject_supplier_profile(request, profile_id):
    """Reject/unapprove a supplier profile."""
    if not request.user.is_superuser:
        messages.error(request, _("Access denied. Superuser permission required."))
        return redirect('users:admin_supplier_profiles')
    
    profile = get_object_or_404(SupplierProfile, id=profile_id)
    
    profile.status = 'pending'
    profile.approved_at = None
    profile.save()
    
    messages.success(request, _(f"Supplier profile status changed to pending for {profile.user.get_full_name()}."))
    return redirect('users:admin_supplier_profiles')


# View names for easier reference
admin_role_applications_view = AdminRoleApplicationsView.as_view()
admin_supplier_profiles_view = AdminSupplierProfilesView.as_view()


# Active roles management views
@method_decorator(staff_member_required, name='dispatch')
class AdminActiveRolesView(ListView):
    """Admin view to manage active roles."""
    model = User
    template_name = "users/admin_active_roles.html"
    context_object_name = "users"
    paginate_by = 20
    
    def get_queryset(self):
        # Only superusers can manage roles
        if not self.request.user.is_superuser:
            messages.error(self.request, _("Access denied. Superuser permission required."))
            return User.objects.none()
        
        # Get all users, but exclude superusers from the list
        queryset = User.objects.exclude(
            is_superuser=True
        ).select_related('organizer_profile', 'supplier_profile').distinct()
        
        # Apply filters
        role_filter = self.request.GET.get('role')
        status_filter = self.request.GET.get('status')
        
        if role_filter == 'organizer':
            queryset = queryset.filter(is_staff=True)
        elif role_filter == 'supplier':
            queryset = queryset.filter(supplier_profile__status='approved')
        elif role_filter == 'basic':
            # Users who are not staff and don't have approved supplier profile
            queryset = queryset.filter(
                is_staff=False
            ).exclude(
                supplier_profile__status='approved'
            )
        
        if status_filter == 'active':
            if role_filter == 'organizer':
                queryset = queryset.filter(is_staff=True, organizer_suspended=False)
            elif role_filter == 'supplier':
                queryset = queryset.filter(supplier_profile__status='approved', supplier_suspended=False)
            elif role_filter == 'basic':
                # Basic users are always "active" unless the account is disabled
                queryset = queryset.filter(is_active=True)
            else:
                queryset = queryset.filter(
                    models.Q(is_staff=True, organizer_suspended=False) |
                    models.Q(supplier_profile__status='approved', supplier_suspended=False) |
                    models.Q(is_staff=False, is_active=True, supplier_profile__isnull=True) |
                    models.Q(is_staff=False, is_active=True, supplier_profile__status__in=['pending', 'rejected'])
                )
        elif status_filter == 'suspended':
            queryset = queryset.filter(
                models.Q(organizer_suspended=True) |
                models.Q(supplier_suspended=True)
            )
        elif status_filter == 'inactive':
            # Show inactive accounts
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('-date_joined')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role_choices'] = [
            ('', _('Todos los usuarios')),
            ('organizer', _('Organizadores')),
            ('supplier', _('Proveedores')),
            ('basic', _('Usuarios Básicos')),
        ]
        context['status_choices'] = [
            ('', _('Todos los estados')),
            ('active', _('Activos')),
            ('suspended', _('Suspendidos')),
            ('inactive', _('Cuentas Inactivas')),
        ]
        context['current_role'] = self.request.GET.get('role', '')
        context['current_status'] = self.request.GET.get('status', '')
        return context


@require_POST
@staff_member_required
def suspend_organizer_role(request, user_id):
    """Suspend organizer role for a user."""
    if not request.user.is_superuser:
        messages.error(request, _("Access denied. Superuser permission required."))
        return redirect('users:admin_active_roles')
    
    user = get_object_or_404(User, id=user_id)
    
    if not user.is_staff:
        messages.error(request, _("User is not an organizer."))
        return redirect('users:admin_active_roles')
    
    if user.organizer_suspended:
        messages.warning(request, _("Organizer role is already suspended."))
        return redirect('users:admin_active_roles')
    
    # Get suspension data from POST
    reason = request.POST.get('reason', '')
    duration_days = request.POST.get('duration_days')
    permanent = request.POST.get('permanent') == 'on'
    
    user.organizer_suspended = True
    user.organizer_suspended_by = request.user
    user.organizer_suspended_at = timezone.now()
    user.organizer_suspension_reason = reason
    
    if not permanent and duration_days:
        from django.utils import timezone
        from datetime import timedelta
        try:
            days = int(duration_days)
            user.organizer_suspended_until = timezone.now() + timedelta(days=days)
        except ValueError:
            pass
    
    user.save()
    
    duration_text = ""
    if permanent:
        duration_text = _(" permanentemente")
    elif user.organizer_suspended_until:
        duration_text = _(" hasta el {}").format(
            user.organizer_suspended_until.strftime("%d/%m/%Y")
        )
    
    messages.success(request, _(f"Rol de organizador suspendido{duration_text} para {user.get_full_name()}."))
    return redirect('users:admin_active_roles')


@require_POST
@staff_member_required
def suspend_supplier_role(request, user_id):
    """Suspend supplier role for a user."""
    if not request.user.is_superuser:
        messages.error(request, _("Access denied. Superuser permission required."))
        return redirect('users:admin_active_roles')
    
    user = get_object_or_404(User, id=user_id)
    
    if not hasattr(user, 'supplier_profile') or user.supplier_profile.status != 'approved':
        messages.error(request, _("User is not an approved supplier."))
        return redirect('users:admin_active_roles')
    
    if user.supplier_suspended:
        messages.warning(request, _("Supplier role is already suspended."))
        return redirect('users:admin_active_roles')
    
    # Get suspension data from POST
    reason = request.POST.get('reason', '')
    duration_days = request.POST.get('duration_days')
    permanent = request.POST.get('permanent') == 'on'
    
    user.supplier_suspended = True
    user.supplier_suspended_by = request.user
    user.supplier_suspended_at = timezone.now()
    user.supplier_suspension_reason = reason
    
    if not permanent and duration_days:
        from django.utils import timezone
        from datetime import timedelta
        try:
            days = int(duration_days)
            user.supplier_suspended_until = timezone.now() + timedelta(days=days)
        except ValueError:
            pass
    
    user.save()
    
    duration_text = ""
    if permanent:
        duration_text = _(" permanentemente")
    elif user.supplier_suspended_until:
        duration_text = _(" hasta el {}").format(
            user.supplier_suspended_until.strftime("%d/%m/%Y")
        )
    
    messages.success(request, _(f"Rol de proveedor suspendido{duration_text} para {user.get_full_name()}."))
    return redirect('users:admin_active_roles')


@require_POST
@staff_member_required
def reactivate_organizer_role(request, user_id):
    """Reactivate suspended organizer role."""
    if not request.user.is_superuser:
        messages.error(request, _("Access denied. Superuser permission required."))
        return redirect('users:admin_active_roles')
    
    user = get_object_or_404(User, id=user_id)
    
    if not user.organizer_suspended:
        messages.warning(request, _("Organizer role is not suspended."))
        return redirect('users:admin_active_roles')
    
    user.organizer_suspended = False
    user.organizer_suspended_until = None
    user.organizer_suspended_by = None
    user.organizer_suspension_reason = ""
    user.save()
    
    messages.success(request, _(f"Rol de organizador reactivado para {user.get_full_name()}."))
    return redirect('users:admin_active_roles')


@require_POST
@staff_member_required
def reactivate_supplier_role(request, user_id):
    """Reactivate suspended supplier role."""
    if not request.user.is_superuser:
        messages.error(request, _("Access denied. Superuser permission required."))
        return redirect('users:admin_active_roles')
    
    user = get_object_or_404(User, id=user_id)
    
    if not user.supplier_suspended:
        messages.warning(request, _("Supplier role is not suspended."))
        return redirect('users:admin_active_roles')
    
    user.supplier_suspended = False
    user.supplier_suspended_until = None
    user.supplier_suspended_by = None
    user.supplier_suspension_reason = ""
    user.save()
    
    messages.success(request, _(f"Rol de proveedor reactivado para {user.get_full_name()}."))
    return redirect('users:admin_active_roles')


@require_POST
@staff_member_required
def revoke_organizer_role(request, user_id):
    """Completely revoke organizer role from a user."""
    if not request.user.is_superuser:
        messages.error(request, _("Access denied. Superuser permission required."))
        return redirect('users:admin_active_roles')
    
    user = get_object_or_404(User, id=user_id)
    
    if not user.is_staff:
        messages.error(request, _("User is not an organizer."))
        return redirect('users:admin_active_roles')
    
    # Remove staff status and clear suspension fields
    user.is_staff = False
    user.organizer_suspended = False
    user.organizer_suspended_until = None
    user.organizer_suspended_by = None
    user.organizer_suspension_reason = ""
    user.save()
    
    # Also delete organizer profile if exists
    if hasattr(user, 'organizer_profile'):
        user.organizer_profile.delete()
    
    messages.success(request, _(f"Rol de organizador revocado completamente para {user.get_full_name()}."))
    return redirect('users:admin_active_roles')


@require_POST
@staff_member_required
def revoke_supplier_role(request, user_id):
    """Completely revoke supplier role from a user."""
    if not request.user.is_superuser:
        messages.error(request, _("Access denied. Superuser permission required."))
        return redirect('users:admin_active_roles')
    
    user = get_object_or_404(User, id=user_id)
    
    if not hasattr(user, 'supplier_profile'):
        messages.error(request, _("User is not a supplier."))
        return redirect('users:admin_active_roles')
    
    # Unapprove supplier profile and clear suspension fields
    user.supplier_profile.status = 'pending'
    user.supplier_profile.approved_at = None
    user.supplier_profile.save()
    
    user.supplier_suspended = False
    user.supplier_suspended_until = None
    user.supplier_suspended_by = None
    user.supplier_suspension_reason = ""
    user.save()
    
    messages.success(request, _(f"Rol de proveedor revocado completamente para {user.get_full_name()}."))
    return redirect('users:admin_active_roles')


# View name for easier reference
admin_active_roles_view = AdminActiveRolesView.as_view()


@require_POST
@staff_member_required
def activate_user_account(request, user_id):
    """Activate a user account."""
    if not request.user.is_superuser:
        messages.error(request, _("Access denied. Superuser permission required."))
        return redirect('users:admin_active_roles')
    
    user = get_object_or_404(User, id=user_id)
    
    if user.is_active:
        messages.warning(request, _("User account is already active."))
        return redirect('users:admin_active_roles')
    
    user.is_active = True
    user.save()
    
    messages.success(request, _(f"Cuenta activada para {user.get_full_name()}."))
    return redirect('users:admin_active_roles')


@require_POST
@staff_member_required
def deactivate_user_account(request, user_id):
    """Deactivate a user account."""
    if not request.user.is_superuser:
        messages.error(request, _("Access denied. Superuser permission required."))
        return redirect('users:admin_active_roles')
    
    user = get_object_or_404(User, id=user_id)
    
    if not user.is_active:
        messages.warning(request, _("User account is already inactive."))
        return redirect('users:admin_active_roles')
    
    # Don't allow deactivating superusers
    if user.is_superuser:
        messages.error(request, _("Cannot deactivate superuser accounts."))
        return redirect('users:admin_active_roles')
    
    reason = request.POST.get('reason', '')
    
    user.is_active = False
    user.save()
    
    # If they have roles, suspend them automatically
    if user.is_staff:
        user.organizer_suspended = True
        user.organizer_suspended_by = request.user
        user.organizer_suspended_at = timezone.now()
        user.organizer_suspension_reason = f"Account deactivated. {reason}".strip()
    
    if user.is_supplier_active:
        user.supplier_suspended = True
        user.supplier_suspended_by = request.user
        user.supplier_suspended_at = timezone.now()
        user.supplier_suspension_reason = f"Account deactivated. {reason}".strip()
    
    user.save()
    
    messages.success(request, _(f"Cuenta desactivada para {user.get_full_name()}."))
    return redirect('users:admin_active_roles')


@require_POST
@staff_member_required
def promote_to_organizer(request, user_id):
    """Promote a basic user to organizer role."""
    if not request.user.is_superuser:
        messages.error(request, _("Access denied. Superuser permission required."))
        return redirect('users:admin_active_roles')
    
    user = get_object_or_404(User, id=user_id)
    
    if user.is_staff:
        messages.warning(request, _("User is already an organizer."))
        return redirect('users:admin_active_roles')
    
    if user.is_superuser:
        messages.error(request, _("Cannot modify superuser accounts."))
        return redirect('users:admin_active_roles')
    
    # Promote to organizer
    user.is_staff = True
    user.organizer_suspended = False
    user.organizer_suspended_by = None
    user.organizer_suspended_at = None
    user.organizer_suspension_reason = ''
    user.save()
    
    # Create organizer profile if it doesn't exist
    organizer_profile, created = OrganizerProfile.objects.get_or_create(
        user=user,
        defaults={
            'bio': f'Organizador en {user.get_full_name()}',
        }
    )
    
    messages.success(request, _(f"{user.get_full_name()} ha sido promovido a Organizador."))
    return redirect('users:admin_active_roles')


@require_POST
@staff_member_required
def approve_as_supplier(request, user_id):
    """Approve a basic user as supplier."""
    if not request.user.is_superuser:
        messages.error(request, _("Access denied. Superuser permission required."))
        return redirect('users:admin_active_roles')
    
    user = get_object_or_404(User, id=user_id)
    
    if user.is_superuser:
        messages.error(request, _("Cannot modify superuser accounts."))
        return redirect('users:admin_active_roles')
    
    # Get or create supplier profile
    supplier_profile, created = SupplierProfile.objects.get_or_create(
        user=user,
        defaults={
            'company_name': user.get_full_name(),
            'status': 'approved',
            'approved_at': timezone.now()
        }
    )
    
    if not created and supplier_profile.status == 'approved':
        messages.warning(request, _("User is already an approved supplier."))
        return redirect('users:admin_active_roles')
    
    # Approve the supplier
    supplier_profile.status = 'approved'
    supplier_profile.approved_at = timezone.now()
    supplier_profile.save()
    
    # Clear any suspensions
    user.supplier_suspended = False
    user.supplier_suspended_by = None
    user.supplier_suspended_at = None
    user.supplier_suspension_reason = ''
    user.save()
    
    messages.success(request, _(f"{user.get_full_name()} ha sido aprobado como Proveedor."))
    return redirect('users:admin_active_roles')
