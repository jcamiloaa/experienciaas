from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField
from django.db.models import EmailField
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for experienciaas.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})


class OrganizerProfile(models.Model):
    """Extended profile for event organizers (staff users)."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="organizer_profile")
    slug = models.SlugField(unique=True, blank=True)
    
    # Profile info
    bio = models.TextField(_("Bio"), blank=True, max_length=1000)
    website = models.URLField(_("Website"), blank=True)
    phone = models.CharField(_("Phone"), max_length=20, blank=True)
    location = models.CharField(_("Location"), max_length=100, blank=True)
    
    # Social media
    facebook_url = models.URLField(_("Facebook"), blank=True)
    twitter_url = models.URLField(_("Twitter"), blank=True)
    instagram_url = models.URLField(_("Instagram"), blank=True)
    linkedin_url = models.URLField(_("LinkedIn"), blank=True)
    
    # Profile image
    avatar = models.ImageField(_("Profile Image"), upload_to="organizers/avatars/", blank=True)
    cover_image = models.ImageField(_("Cover Image"), upload_to="organizers/covers/", blank=True)
    
    # Settings
    is_public = models.BooleanField(_("Public Profile"), default=True)
    allow_contact = models.BooleanField(_("Allow Contact"), default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Organizer Profile")
        verbose_name_plural = _("Organizer Profiles")
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.user.name or self.user.email} - Organizer Profile"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.user.name or self.user.email.split('@')[0])
            self.slug = base_slug
            
            # Ensure uniqueness
            counter = 1
            while OrganizerProfile.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("users:organizer_profile", kwargs={"slug": self.slug})
    
    @property
    def followers_count(self):
        return self.followers.count()
    
    @property
    def events_count(self):
        return self.user.organized_events.filter(status__in=['published', 'sold_out']).count()
    
    @property
    def upcoming_events_count(self):
        from django.utils import timezone
        return self.user.organized_events.filter(
            status__in=['published', 'sold_out'],
            start_date__gte=timezone.now()
        ).count()
    
    @property
    def past_events_count(self):
        from django.utils import timezone
        return self.user.organized_events.filter(
            status__in=['published', 'sold_out'],
            start_date__lt=timezone.now()
        ).count()


class Follow(models.Model):
    """Model for users following organizers."""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    organizer = models.ForeignKey(OrganizerProfile, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['follower', 'organizer']
        verbose_name = _("Follow")
        verbose_name_plural = _("Follows")
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.follower.name or self.follower.email} follows {self.organizer.user.name or self.organizer.user.email}"
