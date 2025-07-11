from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import models
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView, TemplateView
)
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View

from .forms import (
    BulkActionForm, CategoryForm, CityForm, EventFilterForm, EventForm,
    SponsorForm, EventSponsorForm, SponsorshipApplicationForm, SponsorshipApplicationUpdateForm
)
from .models import (
    Category, City, Event, Ticket, Sponsor, EventSponsor, SponsorshipApplication
)


class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to require staff permissions."""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff
    
    def handle_no_permission(self):
        messages.error(self.request, _("You don't have permission to access this area."))
        return redirect('events:list')


class OrganizerRequiredMixin(UserPassesTestMixin):
    """Mixin to require organizer permissions (staff or event organizer)."""
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        # Staff can access everything
        if self.request.user.is_staff:
            return True
        
        # For specific events, check if user is the organizer
        if hasattr(self, 'get_object'):
            try:
                obj = self.get_object()
                # If it's an Event object
                if hasattr(obj, 'organizer'):
                    return obj.organizer == self.request.user
                # If it's an EventSponsor object
                elif hasattr(obj, 'event') and hasattr(obj.event, 'organizer'):
                    return obj.event.organizer == self.request.user
                # If it's a SponsorshipApplication object
                elif hasattr(obj, 'event') and hasattr(obj.event, 'organizer'):
                    return obj.event.organizer == self.request.user
            except:
                pass
        
        # For event-specific views with event_pk
        if 'event_pk' in self.kwargs:
            try:
                event = Event.objects.get(pk=self.kwargs['event_pk'])
                return event.organizer == self.request.user
            except Event.DoesNotExist:
                pass
        
        # For list views, allow organizers to see their own content
        return True
    
    def handle_no_permission(self):
        messages.error(self.request, _("You don't have permission to access this area."))
        return redirect('events:list')


class AdminDashboardView(StaffRequiredMixin, TemplateView):
    """Admin dashboard with event statistics."""
    template_name = "events/admin/dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Event statistics
        total_events = Event.objects.count()
        published_events = Event.objects.filter(status__in=['published', 'sold_out']).count()
        draft_events = Event.objects.filter(status='draft').count()
        featured_events = Event.objects.filter(is_featured=True).count()
        
        # Recent events
        recent_events = Event.objects.select_related('city', 'category').order_by('-created_at')[:5]
        
        # Upcoming events (including sold out)
        upcoming_events = Event.objects.filter(
            status__in=['published', 'sold_out'],
            start_date__gte=timezone.now()
        ).order_by('start_date')[:5]
        
        # Popular events (by tickets, including sold out)
        popular_events = Event.objects.filter(
            status__in=['published', 'sold_out']
        ).annotate(
            ticket_count=Count('tickets')
        ).order_by('-ticket_count')[:5]
        
        context.update({
            'total_events': total_events,
            'published_events': published_events,
            'draft_events': draft_events,
            'featured_events': featured_events,
            'recent_events': recent_events,
            'upcoming_events': upcoming_events,
            'popular_events': popular_events,
        })
        
        return context


class AdminEventListView(StaffRequiredMixin, ListView):
    """Admin view for managing all events."""
    model = Event
    template_name = "events/admin/event_list.html"
    context_object_name = "events"
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Event.objects.select_related('city', 'category', 'organizer').order_by('-created_at')
        
        # Apply filters from GET parameters
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(venue_name__icontains=search)
            )
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        city = self.request.GET.get('city')
        if city:
            queryset = queryset.filter(city_id=city)
        
        price_type = self.request.GET.get('price_type')
        if price_type:
            queryset = queryset.filter(price_type=price_type)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['cities'] = City.objects.filter(is_active=True)
        return context


class AdminBulkActionView(StaffRequiredMixin, TemplateView):
    """Handle bulk actions for events."""
    
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        selected_events = request.POST.getlist('selected_events')
        
        if not action or not selected_events:
            messages.error(request, _("Please select an action and at least one event."))
            return redirect('events:admin_events')
        
        events = Event.objects.filter(id__in=selected_events)
        count = events.count()
        
        if action == 'publish':
            events.update(status='published')
            messages.success(request, f"{count} events published successfully.")
        
        elif action == 'unpublish':
            events.update(status='draft')
            messages.success(request, f"{count} events unpublished successfully.")
        
        elif action == 'feature':
            events.update(is_featured=True)
            messages.success(request, f"{count} events featured successfully.")
        
        elif action == 'unfeature':
            events.update(is_featured=False)
            messages.success(request, f"{count} events unfeatured successfully.")
        
        elif action == 'delete':
            events.delete()
            messages.success(request, f"{count} events deleted successfully.")
        
        else:
            messages.error(request, _("Invalid action selected."))
        
        return redirect('events:admin_events')


class AdminEventCreateView(StaffRequiredMixin, CreateView):
    """Admin view for creating events."""
    model = Event
    form_class = EventForm
    template_name = "events/admin/event_form.html"
    
    def form_valid(self, form):
        form.instance.organizer = self.request.user
        messages.success(self.request, _("Event created successfully!"))
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('events:admin_event_detail', kwargs={'pk': self.object.pk})


class AdminEventUpdateView(StaffRequiredMixin, UpdateView):
    """Admin view for editing events."""
    model = Event
    form_class = EventForm
    template_name = "events/admin/event_form.html"
    context_object_name = "event"
    
    def form_valid(self, form):
        messages.success(self.request, _("Event updated successfully!"))
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('events:admin_event_detail', kwargs={'pk': self.object.pk})


class AdminEventDetailView(StaffRequiredMixin, DetailView):
    """Admin view for event details with management options."""
    model = Event
    template_name = "events/admin/event_detail.html"
    context_object_name = "event"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        
        # Get tickets for this event
        tickets = Ticket.objects.filter(event=event).select_related('user').order_by('-created_at')
        context['tickets'] = tickets
        
        # Get sponsors for this event
        event_sponsors = EventSponsor.objects.filter(event=event).select_related('sponsor').order_by('display_order', 'tier')
        context['event_sponsors'] = event_sponsors
        
        # Get sponsorship applications
        applications = SponsorshipApplication.objects.filter(event=event).order_by('-created_at')
        context['sponsorship_applications'] = applications
        
        # Statistics
        context['stats'] = {
            'total_tickets': tickets.count(),
            'confirmed_tickets': tickets.filter(status='confirmed').count(),
            'pending_tickets': tickets.filter(status='pending').count(),
            'cancelled_tickets': tickets.filter(status='cancelled').count(),
            'total_revenue': sum(ticket.amount_paid for ticket in tickets),
            'sponsors_count': event_sponsors.count(),
            'pending_applications': applications.filter(status='pending').count(),
            'available_sponsor_slots': event.available_sponsor_slots,
        }
        
        return context


class AdminEventDeleteView(StaffRequiredMixin, DeleteView):
    """Admin view for deleting events."""
    model = Event
    template_name = "events/admin/event_confirm_delete.html"
    success_url = reverse_lazy('events:admin_event_list')
    context_object_name = "event"
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Event deleted successfully!"))
        return super().delete(request, *args, **kwargs)


class AdminCategoryListView(StaffRequiredMixin, ListView):
    """Admin view for managing categories."""
    model = Category
    template_name = "events/admin/category_list.html"
    context_object_name = "categories"
    ordering = ['name']


class AdminCategoryCreateView(StaffRequiredMixin, CreateView):
    """Admin view for creating categories."""
    model = Category
    form_class = CategoryForm
    template_name = "events/admin/category_form.html"
    success_url = reverse_lazy('events:admin_category_list')
    
    def form_valid(self, form):
        messages.success(self.request, _("Category created successfully!"))
        return super().form_valid(form)


class AdminCategoryUpdateView(StaffRequiredMixin, UpdateView):
    """Admin view for editing categories."""
    model = Category
    form_class = CategoryForm
    template_name = "events/admin/category_form.html"
    success_url = reverse_lazy('events:admin_category_list')
    
    def form_valid(self, form):
        messages.success(self.request, _("Category updated successfully!"))
        return super().form_valid(form)


class AdminCategoryDeleteView(StaffRequiredMixin, DeleteView):
    """Admin view for deleting categories."""
    model = Category
    template_name = "events/admin/category_confirm_delete.html"
    success_url = reverse_lazy('events:admin_category_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Category deleted successfully!"))
        return super().delete(request, *args, **kwargs)


class AdminCityListView(StaffRequiredMixin, ListView):
    """Admin view for managing cities."""
    model = City
    template_name = "events/admin/city_list.html"
    context_object_name = "cities"
    ordering = ['name']


class AdminCityCreateView(StaffRequiredMixin, CreateView):
    """Admin view for creating cities."""
    model = City
    form_class = CityForm
    template_name = "events/admin/city_form.html"
    success_url = reverse_lazy('events:admin_city_list')
    
    def form_valid(self, form):
        messages.success(self.request, _("City created successfully!"))
        return super().form_valid(form)


class AdminCityUpdateView(StaffRequiredMixin, UpdateView):
    """Admin view for editing cities."""
    model = City
    form_class = CityForm
    template_name = "events/admin/city_form.html"
    success_url = reverse_lazy('events:admin_city_list')
    
    def form_valid(self, form):
        messages.success(self.request, _("City updated successfully!"))
        return super().form_valid(form)


class AdminCityDeleteView(StaffRequiredMixin, DeleteView):
    """Admin view for deleting cities."""
    model = City
    template_name = "events/admin/city_confirm_delete.html"
    success_url = reverse_lazy('events:admin_city_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _("City deleted successfully!"))
        return super().delete(request, *args, **kwargs)


class AdminTicketListView(StaffRequiredMixin, ListView):
    """Admin view for managing tickets."""
    model = Ticket
    template_name = "events/admin/ticket_list.html"
    context_object_name = "tickets"
    paginate_by = 50
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('event', 'user', 'event__city', 'event__category')
        
        # Filter by event if specified in URL path
        event_pk = self.kwargs.get('event_pk')
        if event_pk:
            queryset = queryset.filter(event__pk=event_pk)
        
        # Filter by event if specified in query parameters
        event_slug = self.request.GET.get('event')
        if event_slug:
            queryset = queryset.filter(event__slug=event_slug)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Ticket.STATUS_CHOICES
        context['current_event'] = self.request.GET.get('event')
        context['current_status'] = self.request.GET.get('status')
        
        # Add event information if filtering by event_pk
        event_pk = self.kwargs.get('event_pk')
        if event_pk:
            context['event'] = get_object_or_404(Event, pk=event_pk)
        
        return context


# Sponsor Management Views

class AdminSponsorListView(OrganizerRequiredMixin, ListView):
    """Admin view for managing sponsors."""
    model = Sponsor
    template_name = "events/admin/sponsor_list.html"
    context_object_name = "sponsors"
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Sponsor.objects.order_by('-created_at')
        
        # Apply filters
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(contact_email__icontains=search)
            )
        
        is_approved = self.request.GET.get('is_approved')
        if is_approved:
            queryset = queryset.filter(is_approved=(is_approved == 'true'))
        
        # If not staff, only show sponsors for organizer's events
        if not self.request.user.is_staff:
            # Get events organized by this user
            user_events = Event.objects.filter(organizer=self.request.user)
            # Get sponsors that are linked to these events
            sponsor_ids = EventSponsor.objects.filter(event__in=user_events).values_list('sponsor_id', flat=True)
            queryset = queryset.filter(id__in=sponsor_ids)
        
        return queryset


class AdminSponsorCreateView(StaffRequiredMixin, CreateView):
    """Admin view for creating sponsors."""
    model = Sponsor
    form_class = SponsorForm
    template_name = "events/admin/sponsor_form.html"
    success_url = reverse_lazy('events:admin_sponsor_list')
    
    def form_valid(self, form):
        messages.success(self.request, _("Sponsor created successfully!"))
        return super().form_valid(form)


class AdminSponsorUpdateView(OrganizerRequiredMixin, UpdateView):
    """Admin view for editing sponsors."""
    model = Sponsor
    form_class = SponsorForm
    template_name = "events/admin/sponsor_form.html"
    success_url = reverse_lazy('events:admin_sponsors')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # If not staff, only allow editing sponsors for organizer's events
        if not self.request.user.is_staff:
            user_events = Event.objects.filter(organizer=self.request.user)
            sponsor_ids = EventSponsor.objects.filter(event__in=user_events).values_list('sponsor_id', flat=True)
            queryset = queryset.filter(id__in=sponsor_ids)
        return queryset
    
    def form_valid(self, form):
        messages.success(self.request, _("Sponsor updated successfully!"))
        return super().form_valid(form)
    
    def form_valid(self, form):
        messages.success(self.request, _("Sponsor updated successfully!"))
        return super().form_valid(form)


class AdminSponsorDeleteView(StaffRequiredMixin, DeleteView):
    """Admin view for deleting sponsors."""
    model = Sponsor
    template_name = "events/admin/sponsor_confirm_delete.html"
    success_url = reverse_lazy('events:admin_sponsor_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Sponsor deleted successfully!"))
        return super().delete(request, *args, **kwargs)


# Event Sponsor Management Views

class AdminEventSponsorCreateView(OrganizerRequiredMixin, CreateView):
    """Admin view for adding sponsors to events."""
    model = EventSponsor
    form_class = EventSponsorForm
    template_name = "events/admin/event_sponsor_form.html"
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        event = get_object_or_404(Event, pk=self.kwargs['event_pk'])
        
        # Check if user has permission to manage this event
        if not self.request.user.is_staff and event.organizer != self.request.user:
            messages.error(self.request, _("You don't have permission to manage sponsors for this event."))
            return redirect('events:list')
        
        kwargs['event'] = event
        return kwargs
    
    def form_valid(self, form):
        event = get_object_or_404(Event, pk=self.kwargs['event_pk'])
        form.instance.event = event
        
        # Check if event has available sponsor slots
        if event.available_sponsor_slots <= 0:
            messages.error(self.request, _("No sponsor slots available for this event."))
            return self.form_invalid(form)
        
        messages.success(self.request, _("Sponsor added to event successfully!"))
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('events:admin_event_detail', kwargs={'pk': self.kwargs['event_pk']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = get_object_or_404(Event, pk=self.kwargs['event_pk'])
        return context


class AdminEventSponsorUpdateView(OrganizerRequiredMixin, UpdateView):
    """Admin view for editing event sponsors."""
    model = EventSponsor
    form_class = EventSponsorForm
    template_name = "events/admin/event_sponsor_form.html"
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # If not staff, only allow editing event sponsors for organizer's events
        if not self.request.user.is_staff:
            user_events = Event.objects.filter(organizer=self.request.user)
            queryset = queryset.filter(event__in=user_events)
        return queryset
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.object.event
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, _("Event sponsor updated successfully!"))
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('events:admin_event_detail', kwargs={'pk': self.object.event.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.object.event
        return context


class AdminEventSponsorDeleteView(OrganizerRequiredMixin, DeleteView):
    """Admin view for removing sponsors from events."""
    model = EventSponsor
    template_name = "events/admin/event_sponsor_confirm_delete.html"
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # If not staff, only allow deleting event sponsors for organizer's events
        if not self.request.user.is_staff:
            user_events = Event.objects.filter(organizer=self.request.user)
            queryset = queryset.filter(event__in=user_events)
        return queryset
    
    def get_success_url(self):
        return reverse_lazy('events:admin_event_detail', kwargs={'pk': self.object.event.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Sponsor removed from event successfully!"))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.object.event
        return context


# Sponsorship Application Management Views

class AdminSponsorshipApplicationListView(OrganizerRequiredMixin, ListView):
    """Admin view for managing sponsorship applications."""
    model = SponsorshipApplication
    template_name = "events/admin/sponsorship_application_list.html"
    context_object_name = "applications"
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SponsorshipApplication.objects.select_related('event').order_by('-created_at')
        
        # Apply filters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        event_id = self.request.GET.get('event')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        
        # If not staff, only show applications for organizer's events
        if not self.request.user.is_staff:
            user_events = Event.objects.filter(organizer=self.request.user)
            queryset = queryset.filter(event__in=user_events)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filter events based on user permissions
        if self.request.user.is_staff:
            events = Event.objects.filter(max_sponsors__gt=0).order_by('-created_at')
        else:
            events = Event.objects.filter(organizer=self.request.user, max_sponsors__gt=0).order_by('-created_at')
        
        context['events'] = events
        return context


class AdminSponsorshipApplicationDetailView(OrganizerRequiredMixin, DetailView):
    """Admin view for sponsorship application details."""
    model = SponsorshipApplication
    template_name = "events/admin/sponsorship_application_detail.html"
    context_object_name = "application"
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # If not staff, only allow access to applications for organizer's events
        if not self.request.user.is_staff:
            user_events = Event.objects.filter(organizer=self.request.user)
            queryset = queryset.filter(event__in=user_events)
        return queryset


class AdminSponsorshipApplicationUpdateView(OrganizerRequiredMixin, UpdateView):
    """Admin view for updating sponsorship application status."""
    model = SponsorshipApplication
    form_class = SponsorshipApplicationUpdateForm
    template_name = "events/admin/sponsorship_application_form.html"
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # If not staff, only allow access to applications for organizer's events
        if not self.request.user.is_staff:
            user_events = Event.objects.filter(organizer=self.request.user)
            queryset = queryset.filter(event__in=user_events)
        return queryset
    
    def form_valid(self, form):
        form.instance.reviewed_by = self.request.user
        form.instance.reviewed_at = timezone.now()
        
        # If approved, check if event has available slots
        if form.instance.status == 'approved':
            if form.instance.event.available_sponsor_slots <= 0:
                messages.error(self.request, _("No sponsor slots available for this event."))
                return self.form_invalid(form)
        
        messages.success(self.request, _("Application updated successfully!"))
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('events:admin_sponsorship_application_detail', kwargs={'pk': self.object.pk})


@method_decorator(require_POST, name='dispatch')
class AdminSponsorshipApplicationApproveView(StaffRequiredMixin, View):
    """Admin view for approving sponsorship applications."""
    
    def post(self, request, pk):
        application = get_object_or_404(SponsorshipApplication, pk=pk)
        
        # Check if event has available slots
        if application.event.available_sponsor_slots <= 0:
            messages.error(request, _("No sponsor slots available for this event."))
            return redirect('events:admin_sponsorship_application_detail', pk=pk)
        
        # Create or get sponsor
        sponsor, created = Sponsor.objects.get_or_create(
            contact_email=application.contact_email,
            defaults={
                'name': application.company_name,
                'contact_email': application.contact_email,
                'contact_phone': application.contact_phone,
                'website': application.company_website,
                'description': application.message[:500],  # Truncate to fit
                'is_approved': True,
            }
        )
        
        # Create EventSponsor
        event_sponsor, created = EventSponsor.objects.get_or_create(
            event=application.event,
            sponsor=sponsor,
            defaults={
                'tier': application.proposed_tier,
                'custom_description': application.message[:300],  # Truncate to fit
            }
        )
        
        # Update application status
        application.status = 'approved'
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.save()
        
        if created:
            messages.success(request, _("Application approved and sponsor added to event!"))
        else:
            messages.info(request, _("Application approved. Sponsor was already added to event."))
        
        return redirect('events:admin_sponsorship_application_detail', pk=pk)


@method_decorator(require_POST, name='dispatch')
class AdminSponsorshipApplicationRejectView(StaffRequiredMixin, View):
    """Admin view for rejecting sponsorship applications."""
    
    def post(self, request, pk):
        application = get_object_or_404(SponsorshipApplication, pk=pk)
        
        application.status = 'rejected'
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.save()
        
        messages.success(request, _("Application rejected."))
        return redirect('events:admin_sponsorship_application_detail', pk=pk)
