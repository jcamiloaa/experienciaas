from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import DetailView, ListView, CreateView
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
import random

from .models import Category, City, Event, Ticket, SponsorshipApplication
from .forms import SponsorshipApplicationForm


class EventListView(ListView):
    """List all published events with filtering capabilities."""
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Event.objects.filter(
            status__in=['published', 'sold_out'],
            start_date__gte=timezone.now()
        ).select_related('city', 'category', 'organizer')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(venue_name__icontains=search)
            )
            
            # Track search analytics
            try:
                from experienciaas.analytics.utils import track_search_query
                results_count = queryset.count()
                city = None
                category = None
                
                city_slug = self.request.GET.get('city')
                if city_slug:
                    try:
                        city = City.objects.get(slug=city_slug)
                    except City.DoesNotExist:
                        pass
                
                category_slug = self.request.GET.get('category')
                if category_slug:
                    try:
                        category = Category.objects.get(slug=category_slug)
                    except Category.DoesNotExist:
                        pass
                
                track_search_query(search, results_count, category, city, self.request)
            except ImportError:
                pass
        
        # City filter
        city_slug = self.request.GET.get('city')
        if city_slug:
            queryset = queryset.filter(city__slug=city_slug)
        
        # Category filter
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Date filter
        date_filter = self.request.GET.get('date')
        if date_filter == 'today':
            queryset = queryset.filter(start_date__date=timezone.now().date())
        elif date_filter == 'tomorrow':
            tomorrow = timezone.now().date() + timezone.timedelta(days=1)
            queryset = queryset.filter(start_date__date=tomorrow)
        elif date_filter == 'this_week':
            week_start = timezone.now()
            week_end = week_start + timezone.timedelta(days=7)
            queryset = queryset.filter(start_date__range=[week_start, week_end])
        elif date_filter == 'this_month':
            month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = month_start + timezone.timedelta(days=32)
            month_end = next_month.replace(day=1) - timezone.timedelta(seconds=1)
            queryset = queryset.filter(start_date__range=[month_start, month_end])
        
        # Sort by date or featured
        sort = self.request.GET.get('sort', 'date')
        if sort == 'featured':
            queryset = queryset.order_by('-is_featured', 'start_date')
        else:
            queryset = queryset.order_by('start_date')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cities'] = City.objects.filter(is_active=True, events__isnull=False).distinct()
        context['categories'] = Category.objects.filter(is_active=True, events__isnull=False).distinct()
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'city': self.request.GET.get('city', ''),
            'category': self.request.GET.get('category', ''),
            'date': self.request.GET.get('date', ''),
            'sort': self.request.GET.get('sort', 'date'),
        }
        
        # Get featured events separately - apply same filters as main queryset
        featured_queryset = Event.objects.filter(
            status__in=['published', 'sold_out'],
            start_date__gte=timezone.now(),
            is_featured=True
        ).select_related('city', 'category', 'organizer')
        
        # Apply the same filters to featured events
        search = self.request.GET.get('search')
        if search:
            featured_queryset = featured_queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(venue_name__icontains=search)
            )
        
        city_slug = self.request.GET.get('city')
        if city_slug:
            featured_queryset = featured_queryset.filter(city__slug=city_slug)
        
        category_slug = self.request.GET.get('category')
        if category_slug:
            featured_queryset = featured_queryset.filter(category__slug=category_slug)
        
        date_filter = self.request.GET.get('date')
        if date_filter == 'today':
            featured_queryset = featured_queryset.filter(start_date__date=timezone.now().date())
        elif date_filter == 'tomorrow':
            tomorrow = timezone.now().date() + timezone.timedelta(days=1)
            featured_queryset = featured_queryset.filter(start_date__date=tomorrow)
        elif date_filter == 'this_week':
            week_start = timezone.now()
            week_end = week_start + timezone.timedelta(days=7)
            featured_queryset = featured_queryset.filter(start_date__range=[week_start, week_end])
        elif date_filter == 'this_month':
            month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = month_start + timezone.timedelta(days=32)
            month_end = next_month.replace(day=1) - timezone.timedelta(seconds=1)
            featured_queryset = featured_queryset.filter(start_date__range=[month_start, month_end])
        
        # Order featured events by start date
        context['featured_events'] = featured_queryset.order_by('start_date')
        
        # Add random banner image
        banner_images = [
            'images/banner/experienciaas.png',
            'images/banner/experienciaas_2.png',
            'images/banner/experienciaas_3.png'
        ]
        context['random_banner'] = random.choice(banner_images)
        
        return context


class EventDetailView(DetailView):
    """Display event details."""
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"
    
    def get_queryset(self):
        return Event.objects.filter(status__in=['published', 'sold_out']).select_related(
            'city', 'category', 'organizer'
        )
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        # Track analytics
        try:
            from experienciaas.analytics.utils import track_event_view
            track_event_view(obj, self.request)
        except ImportError:
            pass
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        
        # Check if user already has a ticket
        if self.request.user.is_authenticated:
            context['user_ticket'] = Ticket.objects.filter(
                event=event, 
                user=self.request.user
            ).first()
        
        # Get event sponsors
        from .models import EventSponsor
        context['event_sponsors'] = EventSponsor.objects.filter(
            event=event
        ).select_related('sponsor').order_by('display_order', 'tier')
        
        # Related events (same category or city)
        context['related_events'] = Event.objects.filter(
            Q(category=event.category) | Q(city=event.city),
            status__in=['published', 'sold_out'],
            start_date__gte=timezone.now()
        ).exclude(pk=event.pk)[:4]
        
        return context


class EventsByLocationView(ListView):
    """List events by city."""
    model = Event
    template_name = "events/events_by_location.html"
    context_object_name = "events"
    paginate_by = 12
    
    def get_queryset(self):
        self.city = get_object_or_404(City, slug=self.kwargs['city_slug'])
        return Event.objects.filter(
            city=self.city,
            status__in=['published', 'sold_out'],
            start_date__gte=timezone.now()
        ).select_related('category', 'organizer').order_by('start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['city'] = self.city
        context['categories'] = Category.objects.filter(
            events__city=self.city,
            is_active=True
        ).distinct()
        return context


class EventsByCategoryView(ListView):
    """List events by category."""
    model = Event
    template_name = "events/events_by_category.html"
    context_object_name = "events"
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return Event.objects.filter(
            category=self.category,
            status__in=['published', 'sold_out'],
            start_date__gte=timezone.now()
        ).select_related('city', 'organizer').order_by('start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['cities'] = City.objects.filter(
            events__category=self.category,
            is_active=True
        ).distinct()
        return context


class RegisterForEventView(LoginRequiredMixin, DetailView):
    """Handle event registration."""
    model = Event
    
    def post(self, request, *args, **kwargs):
        event = self.get_object()
        
        # Check if event is available for registration
        if event.status != 'published':
            messages.error(request, _("This event is not available for registration."))
            return redirect(event.get_absolute_url())
        
        if event.start_date <= timezone.now():
            messages.error(request, _("Registration for this event has closed."))
            return redirect(event.get_absolute_url())
        
        # Check if user already registered
        existing_ticket = Ticket.objects.filter(event=event, user=request.user).first()
        if existing_ticket:
            messages.info(request, _("You are already registered for this event."))
            return redirect(event.get_absolute_url())
        
        # Check capacity
        if event.max_attendees and event.attendees_count >= event.max_attendees:
            messages.error(request, _("This event is sold out."))
            return redirect(event.get_absolute_url())
        
        # Create ticket
        ticket = Ticket.objects.create(
            event=event,
            user=request.user,
            attendee_name=request.user.name or request.user.email,
            attendee_email=request.user.email,
            amount_paid=event.price if event.price_type == 'paid' else 0,
            status='confirmed' if event.is_free else 'pending'
        )
        
        if event.is_free:
            messages.success(request, _("You have successfully registered for this event!"))
        else:
            messages.info(request, _("Registration pending payment confirmation."))
        
        return redirect(event.get_absolute_url())


class MyEventsView(LoginRequiredMixin, ListView):
    """Display user's registered events with filtering and calendar view support."""
    template_name = "events/my_events.html"
    context_object_name = "tickets"
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Ticket.objects.filter(user=self.request.user).select_related(
            'event', 'event__city', 'event__category'
        )
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(event__title__icontains=search) |
                Q(event__description__icontains=search) |
                Q(event__venue_name__icontains=search)
            )
        
        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Time filter - set "upcoming" as default if no filter is specified
        time_filter = self.request.GET.get('time_filter')
        now = timezone.now()
        
        # If no time filter is specified, default to 'upcoming'
        if not time_filter:
            time_filter = 'upcoming'
        
        if time_filter == 'upcoming':
            queryset = queryset.filter(event__start_date__gte=now)
        elif time_filter == 'past':
            queryset = queryset.filter(event__start_date__lt=now)
        elif time_filter == 'today':
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timezone.timedelta(days=1)
            queryset = queryset.filter(
                event__start_date__gte=today_start,
                event__start_date__lt=today_end
            )
        elif time_filter == 'this_week':
            week_start = now - timezone.timedelta(days=now.weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            week_end = week_start + timezone.timedelta(days=7)
            queryset = queryset.filter(
                event__start_date__gte=week_start,
                event__start_date__lt=week_end
            )
        
        # Sorting
        sort = self.request.GET.get('sort', '-created_at')
        if sort in ['-created_at', 'event__start_date', 'event__title']:
            queryset = queryset.order_by(sort)
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add statistics for the dashboard
        tickets = self.get_queryset()
        now = timezone.now()
        
        context['stats'] = {
            'total': tickets.count(),
            'confirmed': tickets.filter(status='confirmed').count(),
            'pending': tickets.filter(status='pending').count(),
            'upcoming': tickets.filter(event__start_date__gte=now).count(),
        }
        
        # Add filter information
        context['current_time_filter'] = self.request.GET.get('time_filter', 'upcoming')
        context['current_status_filter'] = self.request.GET.get('status', '')
        context['current_search'] = self.request.GET.get('search', '')
        
        # Check if any non-default filters are active
        has_active_filters = bool(
            self.request.GET.get('time_filter') and self.request.GET.get('time_filter') != 'upcoming' or
            self.request.GET.get('status') or
            self.request.GET.get('search')
        )
        context['has_active_filters'] = has_active_filters
        
        # Check if user has any events at all (without filters)
        all_user_tickets = Ticket.objects.filter(user=self.request.user)
        context['has_any_events'] = all_user_tickets.exists()
        
        return context


class SponsorshipApplicationView(LoginRequiredMixin, CreateView):
    """Handle sponsorship applications."""
    model = SponsorshipApplication
    form_class = SponsorshipApplicationForm
    template_name = "events/sponsorship_application.html"
    success_url = reverse_lazy('events:sponsorship_success')
    
    def form_valid(self, form):
        # Set the user as the applicant
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = get_object_or_404(Event, pk=self.kwargs['event_pk'])
        return context


class SponsorshipSuccessView(DetailView):
    """Display sponsorship application success message."""
    model = SponsorshipApplication
    template_name = "events/sponsorship_success.html"
    context_object_name = "application"
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = get_object_or_404(Event, pk=self.kwargs['event_pk'])
        return context


class SponsorshipApplicationCreateView(LoginRequiredMixin, CreateView):
    """View for creating sponsorship applications - requires approved supplier profile."""
    model = SponsorshipApplication
    form_class = SponsorshipApplicationForm
    template_name = "events/sponsorship_application_form.html"
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user has approved supplier profile
        if not request.user.is_authenticated:
            return redirect('account_login')
        
        if not hasattr(request.user, 'supplier_profile'):
            messages.error(request, _("Necesitas tener un perfil de proveedor para aplicar a patrocinios. Primero solicita ser proveedor."))
            return redirect('users:apply_for_role')
        
        if not request.user.supplier_profile.is_approved:
            messages.error(request, _("Tu perfil de proveedor debe estar aprobado para aplicar a patrocinios. Estado actual: {status}").format(
                status=_("Pendiente de aprobación") if not request.user.supplier_profile.is_approved else _("Aprobado")
            ))
            return redirect('users:profile')
        
        # Check if supplier role is active (not suspended)
        if not request.user.is_supplier_active:
            suspension_msg = ""
            if request.user.supplier_suspended_until:
                suspension_msg = _(" hasta el {}").format(request.user.supplier_suspended_until.strftime("%d/%m/%Y"))
            elif request.user.supplier_suspended:
                suspension_msg = _(" de forma permanente")
            
            messages.error(request, _("Tu rol de proveedor está suspendido{suspension}. No puedes aplicar a patrocinios.").format(
                suspension=suspension_msg
            ))
            return redirect('users:profile')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = get_object_or_404(Event, slug=self.kwargs['event_slug'])
        kwargs['supplier_profile'] = self.request.user.supplier_profile
        return kwargs
    
    def form_valid(self, form):
        event = get_object_or_404(Event, slug=self.kwargs['event_slug'])
        supplier_profile = self.request.user.supplier_profile
        
        # Check if sponsorship is available
        if not event.sponsorship_available:
            messages.error(self.request, _("Las aplicaciones de patrocinio no están disponibles para este evento."))
            return redirect(event.get_absolute_url())
        
        # Check if supplier already applied
        if SponsorshipApplication.objects.filter(
            event=event,
            contact_email=supplier_profile.business_email or supplier_profile.user.email
        ).exists():
            messages.error(self.request, _("Ya has aplicado para patrocinar este evento."))
            return redirect(event.get_absolute_url())
        
        # Auto-fill company information from supplier profile
        form.instance.event = event
        form.instance.company_name = supplier_profile.company_name
        form.instance.contact_name = supplier_profile.contact_person or supplier_profile.user.name or supplier_profile.user.email
        form.instance.contact_email = supplier_profile.business_email or supplier_profile.user.email
        form.instance.contact_phone = supplier_profile.business_phone or supplier_profile.user.full_phone
        form.instance.company_website = supplier_profile.company_website
        
        messages.success(self.request, _("Tu solicitud de patrocinio ha sido enviada exitosamente! El organizador del evento te contactará pronto."))
        return super().form_valid(form)
    
    def get_success_url(self):
        return self.object.event.get_absolute_url()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = get_object_or_404(Event, slug=self.kwargs['event_slug'])
        context['supplier_profile'] = self.request.user.supplier_profile
        return context
