from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.utils import timezone
import datetime

from .utils import get_organizer_analytics, get_platform_analytics
from .models import DailyStats, OrganizerStats
from experienciaas.users.models import OrganizerProfile


class OrganizerAnalyticsView(LoginRequiredMixin, TemplateView):
    """Analytics dashboard for organizers."""
    template_name = 'analytics/organizer_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get organizer profile
        organizer = get_object_or_404(
            OrganizerProfile,
            user=self.request.user
        )
        
        # Get time period from request
        days = int(self.request.GET.get('days', 30))
        
        # Get analytics data
        analytics = get_organizer_analytics(organizer, days)
        
        context.update({
            'organizer': organizer,
            'analytics': analytics,
            'days': days
        })
        
        return context


@method_decorator(staff_member_required, name='dispatch')
class PlatformAnalyticsView(TemplateView):
    """Platform analytics dashboard for admin users."""
    template_name = 'analytics/platform_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get time period from request
        days = int(self.request.GET.get('days', 30))
        
        # Get analytics data
        analytics = get_platform_analytics(days)
        
        # Get recent daily stats
        recent_stats = DailyStats.objects.order_by('-date')[:days]
        
        context.update({
            'analytics': analytics,
            'recent_stats': recent_stats,
            'days': days
        })
        
        return context


def organizer_analytics_api(request):
    """API endpoint for organizer analytics data."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    organizer = get_object_or_404(
        OrganizerProfile,
        user=request.user
    )
    
    days = int(request.GET.get('days', 30))
    analytics = get_organizer_analytics(organizer, days)
    
    # Format data for charts
    daily_views_data = {
        'labels': [item['day'].strftime('%Y-%m-%d') for item in analytics['daily_views']],
        'data': [item['views'] for item in analytics['daily_views']]
    }
    
    return JsonResponse({
        'success': True,
        'data': {
            'total_events': analytics['total_events'],
            'published_events': analytics['published_events'],
            'upcoming_events': analytics['upcoming_events'],
            'recent_event_views': analytics['recent_event_views'],
            'profile_views': analytics['profile_views'],
            'total_followers': analytics['total_followers'],
            'new_followers': analytics['new_followers'],
            'tickets_sold': analytics['tickets_sold'],
            'revenue': float(analytics['revenue']),
            'daily_views': daily_views_data,
            'top_events': [
                {
                    'title': event.title,
                    'views': event.views_count,
                    'tickets': event.tickets_count
                }
                for event in analytics['top_events']
            ]
        }
    })


@staff_member_required
def platform_analytics_api(request):
    """API endpoint for platform analytics data."""
    days = int(request.GET.get('days', 30))
    analytics = get_platform_analytics(days)
    
    # Get daily stats for chart
    end_date = timezone.now().date()
    start_date = end_date - datetime.timedelta(days=days)
    
    daily_stats = DailyStats.objects.filter(
        date__range=(start_date, end_date)
    ).order_by('date')
    
    daily_data = {
        'labels': [stat.date.strftime('%Y-%m-%d') for stat in daily_stats],
        'new_events': [stat.new_events for stat in daily_stats],
        'new_users': [stat.new_users for stat in daily_stats],
        'new_tickets': [stat.new_tickets for stat in daily_stats],
        'new_revenue': [float(stat.new_revenue) for stat in daily_stats],
        'total_views': [stat.total_views for stat in daily_stats],
    }
    
    return JsonResponse({
        'success': True,
        'data': {
            'summary': {
                'total_events': analytics['total_events'],
                'new_events': analytics['new_events'],
                'total_users': analytics['total_users'],
                'new_users': analytics['new_users'],
                'total_tickets': analytics['total_tickets'],
                'new_tickets': analytics['new_tickets'],
                'total_revenue': float(analytics['total_revenue']),
                'new_revenue': float(analytics['new_revenue']),
                'total_views': analytics['total_views'],
                'new_views': analytics['new_views'],
            },
            'daily_data': daily_data,
            'popular_searches': [
                {
                    'query': item['query'],
                    'count': item['count']
                }
                for item in analytics['popular_searches']
            ]
        }
    })


organizer_analytics_view = OrganizerAnalyticsView.as_view()
platform_analytics_view = PlatformAnalyticsView.as_view()
