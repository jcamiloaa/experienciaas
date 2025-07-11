from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
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

from experienciaas.users.models import User, OrganizerProfile, Follow


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

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
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


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
