from django.utils.deprecation import MiddlewareMixin
from experienciaas.analytics.utils import track_event_view, track_organizer_view


class AnalyticsMiddleware(MiddlewareMixin):
    """Middleware to automatically track page views for analytics."""
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Track event views
        if 'events.views' in str(view_func) and 'detail' in view_func.__name__.lower():
            # This will be handled in the view itself to avoid duplicate tracking
            pass
        
        # Track organizer profile views
        if 'users.views' in str(view_func) and 'organizer' in view_func.__name__.lower():
            # This will be handled in the view itself to avoid duplicate tracking
            pass
        
        return None
