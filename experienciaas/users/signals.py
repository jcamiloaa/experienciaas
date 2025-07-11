from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import OrganizerProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_or_update_organizer_profile(sender, instance, created, **kwargs):
    """Create or update organizer profile when user becomes staff."""
    if instance.is_staff:
        # Create organizer profile if it doesn't exist
        if not hasattr(instance, 'organizer_profile'):
            OrganizerProfile.objects.create(user=instance)
    else:
        # If user is no longer staff, optionally hide their profile
        if hasattr(instance, 'organizer_profile'):
            instance.organizer_profile.is_public = False
            instance.organizer_profile.save()
