from typing import ClassVar
import re
from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField
from django.db.models import EmailField
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError

from .managers import UserManager


# Country codes for phone numbers
COUNTRY_CHOICES = [
    ('+1', _('Estados Unidos (+1)')),
    ('+1', _('Canadá (+1)')),
    ('+52', _('México (+52)')),
    ('+34', _('España (+34)')),
    ('+33', _('Francia (+33)')),
    ('+49', _('Alemania (+49)')),
    ('+39', _('Italia (+39)')),
    ('+44', _('Reino Unido (+44)')),
    ('+54', _('Argentina (+54)')),
    ('+55', _('Brasil (+55)')),
    ('+56', _('Chile (+56)')),
    ('+57', _('Colombia (+57)')),
    ('+58', _('Venezuela (+58)')),
    ('+51', _('Perú (+51)')),
    ('+593', _('Ecuador (+593)')),
    ('+598', _('Uruguay (+598)')),
    ('+595', _('Paraguay (+595)')),
    ('+591', _('Bolivia (+591)')),
]

GENDER_CHOICES = [
    ('M', _('Masculino')),
    ('F', _('Femenino')),
    ('O', _('Otro')),
    ('N', _('Prefiero no decir')),
]

INTEREST_CHOICES = [
    ('music', _('Música')),
    ('technology', _('Tecnología')),
    ('sports', _('Deportes')),
    ('art', _('Arte')),
    ('food', _('Gastronomía')),
    ('travel', _('Viajes')),
    ('business', _('Negocios')),
    ('education', _('Educación')),
    ('health', _('Salud y Bienestar')),
    ('gaming', _('Videojuegos')),
    ('photography', _('Fotografía')),
    ('fashion', _('Moda')),
    ('books', _('Libros y Literatura')),
    ('movies', _('Cine')),
    ('outdoors', _('Actividades al Aire Libre')),
    ('science', _('Ciencia')),
    ('culture', _('Cultura')),
    ('networking', _('Networking')),
]


def validate_birth_date(value):
    """Validate that birth date is reasonable."""
    if value:
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 13:
            raise ValidationError(_('Debes tener al menos 13 años para registrarte.'))
        if age > 120:
            raise ValidationError(_('Por favor, introduce una fecha de nacimiento válida.'))


class User(AbstractUser):
    """
    Enhanced custom user model for experienciaas event platform.
    Includes personal information, contact details, location, and preferences.
    """

    # Basic Information
    name = CharField(_("Nombre completo"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]
    
    # Personal Details
    birth_date = models.DateField(
        _("Fecha de nacimiento"), 
        blank=True, 
        null=True,
        validators=[validate_birth_date],
        help_text=_("Formato: AAAA-MM-DD")
    )
    gender = models.CharField(
        _("Género"), 
        max_length=1, 
        choices=GENDER_CHOICES, 
        blank=True,
        help_text=_("Esta información es opcional y privada")
    )
    bio = models.TextField(
        _("Biografía"), 
        blank=True, 
        max_length=500,
        help_text=_("Cuéntanos un poco sobre ti (máximo 500 caracteres)")
    )
    
    # Contact Information
    country_code = models.CharField(
        _("Código de país"), 
        max_length=5, 
        choices=COUNTRY_CHOICES, 
        default='+57',
        help_text=_("Selecciona el código de tu país")
    )
    phone_validator = RegexValidator(
        regex=r'^\d{7,15}$',
        message=_("El número de teléfono debe contener entre 7 y 15 dígitos.")
    )
    phone_number = models.CharField(
        _("Número de teléfono"), 
        max_length=15, 
        blank=True,
        validators=[phone_validator],
        help_text=_("Solo números, sin espacios ni guiones")
    )
    
    # Location Information
    country = models.CharField(
        _("País"), 
        max_length=100, 
        blank=True,
        help_text=_("País de residencia")
    )
    city = models.CharField(
        _("Ciudad"), 
        max_length=100, 
        blank=True,
        help_text=_("Ciudad de residencia")
    )
    address = models.CharField(
        _("Dirección"), 
        max_length=255, 
        blank=True,
        help_text=_("Dirección completa (opcional)")
    )
    postal_code = models.CharField(
        _("Código postal"), 
        max_length=20, 
        blank=True
    )
    
    # Professional Information
    occupation = models.CharField(
        _("Ocupación"), 
        max_length=100, 
        blank=True,
        help_text=_("Tu profesión o trabajo actual")
    )
    company = models.CharField(
        _("Empresa"), 
        max_length=100, 
        blank=True,
        help_text=_("Empresa donde trabajas (opcional)")
    )
    website = models.URLField(
        _("Sitio web"), 
        blank=True,
        help_text=_("Tu sitio web personal o profesional")
    )
    
    # Social Media
    linkedin_url = models.URLField(_("LinkedIn"), blank=True)
    twitter_url = models.URLField(_("Twitter/X"), blank=True)
    instagram_url = models.URLField(_("Instagram"), blank=True)
    facebook_url = models.URLField(_("Facebook"), blank=True)
    
    # Interests and Preferences
    interests = models.JSONField(
        _("Intereses"), 
        default=list, 
        blank=True,
        help_text=_("Selecciona tus áreas de interés para eventos")
    )
    hobbies = models.TextField(
        _("Hobbies"), 
        blank=True, 
        max_length=300,
        help_text=_("Describe tus hobbies e intereses personales")
    )
    
    # Profile Image
    avatar = models.ImageField(
        _("Foto de perfil"), 
        upload_to="users/avatars/", 
        blank=True,
        help_text=_("Imagen de perfil (recomendado: 400x400px)")
    )
    
    # Privacy Settings
    profile_visible = models.BooleanField(
        _("Perfil público"), 
        default=True,
        help_text=_("Si tu perfil es visible para otros usuarios")
    )
    show_email = models.BooleanField(
        _("Mostrar email"), 
        default=False,
        help_text=_("Si otros usuarios pueden ver tu email")
    )
    show_phone = models.BooleanField(
        _("Mostrar teléfono"), 
        default=False,
        help_text=_("Si otros usuarios pueden ver tu teléfono")
    )
    
    # Notification Preferences
    email_notifications = models.BooleanField(
        _("Notificaciones por email"), 
        default=True,
        help_text=_("Recibir notificaciones de eventos por email")
    )
    sms_notifications = models.BooleanField(
        _("Notificaciones por SMS"), 
        default=False,
        help_text=_("Recibir notificaciones importantes por SMS")
    )
    marketing_emails = models.BooleanField(
        _("Emails promocionales"), 
        default=False,
        help_text=_("Recibir información sobre eventos y promociones")
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    class Meta:
        verbose_name = _("Usuario")
        verbose_name_plural = _("Usuarios")
        ordering = ["-date_joined"]

    def __str__(self):
        return self.name or self.email

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})
    
    @property
    def full_phone(self):
        """Return complete phone number with country code."""
        if self.phone_number:
            return f"{self.country_code} {self.phone_number}"
        return ""
    
    @property
    def age(self):
        """Calculate user's age from birth date."""
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None
    
    @property
    def location(self):
        """Return formatted location string."""
        parts = []
        if self.city:
            parts.append(self.city)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts) if parts else ""
    
    def get_interests_display(self):
        """Return display names for selected interests."""
        if not self.interests:
            return []
        interest_dict = dict(INTEREST_CHOICES)
        return [interest_dict.get(interest, interest) for interest in self.interests]


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
