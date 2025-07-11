import datetime
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import (
    EventView, OrganizerView, SearchQuery, TicketRegistration,
    DailyStats, OrganizerStats
)
from experienciaas.events.models import Event, Ticket
from experienciaas.users.models import OrganizerProfile

User = get_user_model()


def track_event_view(event, request):
    """Track an event page view."""
    user = request.user if request.user.is_authenticated else None
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    referrer = request.META.get('HTTP_REFERER', '')
    
    EventView.objects.create(
        event=event,
        user=user,
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=referrer
    )
    
    # Update event view count
    event.views += 1
    event.save(update_fields=['views'])


def track_organizer_view(organizer, request):
    """Track an organizer profile view."""
    user = request.user if request.user.is_authenticated else None
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    referrer = request.META.get('HTTP_REFERER', '')
    
    OrganizerView.objects.create(
        organizer=organizer,
        user=user,
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=referrer
    )


def track_search_query(query, results_count, category=None, city=None, request=None):
    """Track a search query."""
    user = request.user if request and request.user.is_authenticated else None
    ip_address = get_client_ip(request) if request else '127.0.0.1'
    
    SearchQuery.objects.create(
        query=query,
        user=user,
        ip_address=ip_address,
        results_count=results_count,
        category=category,
        city=city
    )


def track_ticket_registration(event, step, request, session_id=None):
    """Track ticket registration funnel."""
    user = request.user if request.user.is_authenticated else None
    ip_address = get_client_ip(request)
    
    if not session_id:
        session_id = request.session.session_key
    
    TicketRegistration.objects.create(
        event=event,
        user=user,
        session_id=session_id,
        step=step,
        ip_address=ip_address
    )


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_organizer_analytics(organizer, days=30):
    """Get comprehensive analytics for an organizer."""
    end_date = timezone.now()
    start_date = end_date - datetime.timedelta(days=days)
    
    # Event metrics
    total_events = organizer.user.organized_events.count()
    published_events = organizer.user.organized_events.filter(status='published').count()
    upcoming_events = organizer.user.organized_events.filter(
        status='published',
        start_date__gte=timezone.now()
    ).count()
    
    # Recent event views
    recent_event_views = EventView.objects.filter(
        event__organizer=organizer.user,
        timestamp__gte=start_date
    ).count()
    
    # Profile views
    profile_views = OrganizerView.objects.filter(
        organizer=organizer,
        timestamp__gte=start_date
    ).count()
    
    # Follower growth
    total_followers = organizer.followers_count
    new_followers = organizer.followers.filter(
        created_at__gte=start_date
    ).count()
    
    # Ticket sales
    tickets_sold = Ticket.objects.filter(
        event__organizer=organizer.user,
        status='confirmed',
        created_at__gte=start_date
    ).count()
    
    # Revenue
    revenue = Ticket.objects.filter(
        event__organizer=organizer.user,
        status='confirmed',
        created_at__gte=start_date
    ).aggregate(
        total_revenue=Sum('amount_paid')
    )['total_revenue'] or 0
    
    # Top performing events
    top_events = organizer.user.organized_events.filter(
        status='published'
    ).annotate(
        views_count=Count('event_views'),
        tickets_count=Count('tickets', filter=Q(tickets__status='confirmed'))
    ).order_by('-views_count')[:5]
    
    # Engagement by day
    daily_views = EventView.objects.filter(
        event__organizer=organizer.user,
        timestamp__gte=start_date
    ).extra(
        select={'day': 'date(timestamp)'}
    ).values('day').annotate(
        views=Count('id')
    ).order_by('day')
    
    return {
        'total_events': total_events,
        'published_events': published_events,
        'upcoming_events': upcoming_events,
        'recent_event_views': recent_event_views,
        'profile_views': profile_views,
        'total_followers': total_followers,
        'new_followers': new_followers,
        'tickets_sold': tickets_sold,
        'revenue': revenue,
        'top_events': top_events,
        'daily_views': daily_views,
        'period_days': days
    }


def get_platform_analytics(days=30):
    """Get platform-wide analytics."""
    end_date = timezone.now()
    start_date = end_date - datetime.timedelta(days=days)
    
    # Events
    total_events = Event.objects.count()
    new_events = Event.objects.filter(created_at__gte=start_date).count()
    published_events = Event.objects.filter(status='published').count()
    
    # Users
    total_users = User.objects.count()
    new_users = User.objects.filter(date_joined__gte=start_date).count()
    staff_users = User.objects.filter(is_staff=True).count()
    
    # Organizers
    total_organizers = OrganizerProfile.objects.count()
    public_organizers = OrganizerProfile.objects.filter(is_public=True).count()
    
    # Tickets
    total_tickets = Ticket.objects.count()
    new_tickets = Ticket.objects.filter(created_at__gte=start_date).count()
    confirmed_tickets = Ticket.objects.filter(status='confirmed').count()
    
    # Revenue
    total_revenue = Ticket.objects.filter(status='confirmed').aggregate(
        total=Sum('amount_paid')
    )['total'] or 0
    
    new_revenue = Ticket.objects.filter(
        status='confirmed',
        created_at__gte=start_date
    ).aggregate(
        total=Sum('amount_paid')
    )['total'] or 0
    
    # Views
    total_views = EventView.objects.count()
    new_views = EventView.objects.filter(timestamp__gte=start_date).count()
    
    # Popular searches
    popular_searches = SearchQuery.objects.filter(
        timestamp__gte=start_date
    ).values('query').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    return {
        'total_events': total_events,
        'new_events': new_events,
        'published_events': published_events,
        'total_users': total_users,
        'new_users': new_users,
        'staff_users': staff_users,
        'total_organizers': total_organizers,
        'public_organizers': public_organizers,
        'total_tickets': total_tickets,
        'new_tickets': new_tickets,
        'confirmed_tickets': confirmed_tickets,
        'total_revenue': total_revenue,
        'new_revenue': new_revenue,
        'total_views': total_views,
        'new_views': new_views,
        'popular_searches': popular_searches,
        'period_days': days
    }


def generate_daily_stats(date=None):
    """Generate daily statistics for a specific date."""
    if date is None:
        date = timezone.now().date()
    
    start_of_day = datetime.datetime.combine(date, datetime.time.min)
    end_of_day = datetime.datetime.combine(date, datetime.time.max)
    
    # Make timezone aware
    start_of_day = timezone.make_aware(start_of_day)
    end_of_day = timezone.make_aware(end_of_day)
    
    # Event stats
    total_events = Event.objects.filter(created_at__date__lte=date).count()
    new_events = Event.objects.filter(created_at__date=date).count()
    published_events = Event.objects.filter(
        status='published',
        created_at__date__lte=date
    ).count()
    
    # User stats
    total_users = User.objects.filter(date_joined__date__lte=date).count()
    new_users = User.objects.filter(date_joined__date=date).count()
    active_users = User.objects.filter(
        last_login__range=(start_of_day, end_of_day)
    ).count()
    
    # Ticket stats
    total_tickets = Ticket.objects.filter(created_at__date__lte=date).count()
    new_tickets = Ticket.objects.filter(created_at__date=date).count()
    confirmed_tickets = Ticket.objects.filter(
        status='confirmed',
        created_at__date__lte=date
    ).count()
    
    # Revenue stats
    total_revenue = Ticket.objects.filter(
        status='confirmed',
        created_at__date__lte=date
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    new_revenue = Ticket.objects.filter(
        status='confirmed',
        created_at__date=date
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    # Traffic stats
    total_views = EventView.objects.filter(timestamp__date__lte=date).count()
    unique_visitors = EventView.objects.filter(
        timestamp__range=(start_of_day, end_of_day)
    ).values('ip_address').distinct().count()
    
    # Update or create daily stats
    daily_stats, created = DailyStats.objects.update_or_create(
        date=date,
        defaults={
            'total_events': total_events,
            'new_events': new_events,
            'published_events': published_events,
            'total_users': total_users,
            'new_users': new_users,
            'active_users': active_users,
            'total_tickets': total_tickets,
            'new_tickets': new_tickets,
            'confirmed_tickets': confirmed_tickets,
            'total_revenue': total_revenue,
            'new_revenue': new_revenue,
            'total_views': total_views,
            'unique_visitors': unique_visitors,
        }
    )
    
    return daily_stats
