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
    
    # Role Management and Suspension
    organizer_suspended = models.BooleanField(
        _("Rol de organizador suspendido"), 
        default=False,
        help_text=_("Si el rol de organizador está temporalmente suspendido")
    )
    organizer_suspended_until = models.DateTimeField(
        _("Suspendido hasta"), 
        blank=True, 
        null=True,
        help_text=_("Fecha hasta la cual está suspendido el rol de organizador")
    )
    organizer_suspended_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='organizer_suspensions_made',
        verbose_name=_("Suspendido por"),
        help_text=_("Administrador que suspendió el rol de organizador")
    )
    organizer_suspension_reason = models.TextField(
        _("Razón de suspensión de organizador"), 
        blank=True,
        help_text=_("Motivo de la suspensión del rol de organizador")
    )
    
    supplier_suspended = models.BooleanField(
        _("Rol de proveedor suspendido"), 
        default=False,
        help_text=_("Si el rol de proveedor está temporalmente suspendido")
    )
    supplier_suspended_until = models.DateTimeField(
        _("Suspendido hasta"), 
        blank=True, 
        null=True,
        help_text=_("Fecha hasta la cual está suspendido el rol de proveedor")
    )
    supplier_suspended_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='supplier_suspensions_made',
        verbose_name=_("Suspendido por"),
        help_text=_("Administrador que suspendió el rol de proveedor")
    )
    supplier_suspension_reason = models.TextField(
        _("Razón de suspensión de proveedor"), 
        blank=True,
        help_text=_("Motivo de la suspensión del rol de proveedor")
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
    
    # Role checking properties
    @property
    def is_organizer(self):
        """Check if user has organizer role (is staff and has organizer profile)."""
        return self.is_staff and hasattr(self, 'organizer_profile')
    
    @property
    def is_organizer_active(self):
        """Check if user has active organizer role (not suspended)."""
        from django.utils import timezone
        if not self.is_organizer:
            return False
        if not self.organizer_suspended:
            return True
        # Check if suspension period has expired
        if self.organizer_suspended_until and timezone.now() > self.organizer_suspended_until:
            # Auto-reactivate if suspension period has expired
            self.organizer_suspended = False
            self.organizer_suspended_until = None
            self.organizer_suspended_by = None
            self.organizer_suspension_reason = ""
            self.save(update_fields=[
                'organizer_suspended', 'organizer_suspended_until', 
                'organizer_suspended_by', 'organizer_suspension_reason'
            ])
            return True
        return False
    
    @property
    def is_supplier(self):
        """Check if user has approved supplier role."""
        return (hasattr(self, 'supplier_profile') and 
                self.supplier_profile.is_approved)
    
    @property
    def is_supplier_active(self):
        """Check if user has active supplier role (approved and not suspended)."""
        from django.utils import timezone
        if not self.is_supplier:
            return False
        if not self.supplier_suspended:
            return True
        # Check if suspension period has expired
        if self.supplier_suspended_until and timezone.now() > self.supplier_suspended_until:
            # Auto-reactivate if suspension period has expired
            self.supplier_suspended = False
            self.supplier_suspended_until = None
            self.supplier_suspended_by = None
            self.supplier_suspension_reason = ""
            self.save(update_fields=[
                'supplier_suspended', 'supplier_suspended_until', 
                'supplier_suspended_by', 'supplier_suspension_reason'
            ])
            return True
        return False
    
    @property
    def is_admin(self):
        """Check if user is admin (superuser)."""
        return self.is_superuser
    
    @property
    def has_pending_organizer_application(self):
        """Check if user has pending organizer application."""
        return self.role_applications.filter(
            role='organizer', 
            status='pending'
        ).exists()
    
    @property
    def has_pending_supplier_application(self):
        """Check if user has pending supplier application."""
        return self.role_applications.filter(
            role='supplier', 
            status='pending'
        ).exists()
    
    @property
    def can_apply_for_organizer(self):
        """Check if user can apply for organizer role."""
        return (not self.is_organizer and 
                not self.has_pending_organizer_application)
    
    @property
    def can_apply_for_supplier(self):
        """Check if user can apply for supplier role."""
        # Can apply if:
        # 1. Not currently an approved supplier
        # 2. No pending application
        # 3. Either no supplier profile OR supplier profile is rejected/suspended
        if self.is_supplier:
            return False
        if self.has_pending_supplier_application:
            return False
        if hasattr(self, 'supplier_profile'):
            # Can reapply if profile was rejected or suspended
            return self.supplier_profile.status in ['rejected', 'suspended']
        return True
    
    def get_role_display(self):
        """Get user's current role for display."""
        roles = []
        if self.is_admin:
            roles.append(_("Administrador"))
        if self.is_organizer:
            roles.append(_("Organizador"))
        if self.is_supplier:
            roles.append(_("Proveedor"))
        
        if not roles:
            return _("Usuario")
        
        return " + ".join(roles)


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


class SupplierProfile(models.Model):
    """Extended profile for suppliers/sponsors."""
    STATUS_CHOICES = [
        ('pending', _('Pending Approval')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('suspended', _('Suspended')),
    ]
    
    COMPANY_SIZE_CHOICES = [
        ('startup', _('Startup (1-10 empleados)')),
        ('small', _('Pequeña (11-50 empleados)')),
        ('medium', _('Mediana (51-200 empleados)')),
        ('large', _('Grande (201-1000 empleados)')),
        ('enterprise', _('Empresa (1000+ empleados)')),
    ]
    
    INDUSTRY_CHOICES = [
        ('technology', _('Tecnología')),
        ('marketing', _('Marketing y Publicidad')),
        ('food', _('Alimentos y Bebidas')),
        ('fashion', _('Moda y Retail')),
        ('finance', _('Servicios Financieros')),
        ('health', _('Salud y Bienestar')),
        ('education', _('Educación')),
        ('entertainment', _('Entretenimiento')),
        ('sports', _('Deportes')),
        ('automotive', _('Automotriz')),
        ('real_estate', _('Bienes Raíces')),
        ('consulting', _('Consultoría')),
        ('manufacturing', _('Manufactura')),
        ('logistics', _('Logística y Transporte')),
        ('energy', _('Energía')),
        ('telecommunications', _('Telecomunicaciones')),
        ('media', _('Medios de Comunicación')),
        ('nonprofit', _('Organización Sin Fines de Lucro')),
        ('government', _('Gobierno')),
        ('other', _('Otro')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="supplier_profile")
    slug = models.SlugField(unique=True, blank=True)
    
    # Application info
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='pending')
    application_reason = models.TextField(
        _("Razón de la aplicación"), 
        max_length=1000,
        help_text=_("Explica por qué quieres ser un proveedor/patrocinador en nuestra plataforma")
    )
    
    # Company information
    company_name = models.CharField(_("Nombre de la empresa"), max_length=200)
    company_description = models.TextField(_("Descripción de la empresa"), max_length=1000, blank=True)
    company_size = models.CharField(_("Tamaño de la empresa"), max_length=20, choices=COMPANY_SIZE_CHOICES, blank=True)
    industry = models.CharField(_("Industria"), max_length=50, choices=INDUSTRY_CHOICES, blank=True)
    founding_year = models.PositiveIntegerField(_("Año de fundación"), blank=True, null=True)
    
    # Legal information
    tax_id = models.CharField(_("NIT/RUT"), max_length=50, blank=True)
    legal_address = models.CharField(_("Dirección legal"), max_length=255, blank=True)
    
    # Contact information
    business_phone = models.CharField(_("Teléfono empresarial"), max_length=20, blank=True)
    business_email = models.EmailField(_("Email empresarial"), blank=True)
    contact_person = models.CharField(_("Persona de contacto"), max_length=100, blank=True)
    contact_position = models.CharField(_("Cargo del contacto"), max_length=100, blank=True)
    
    # Online presence
    company_website = models.URLField(_("Sitio web de la empresa"), blank=True)
    facebook_url = models.URLField(_("Facebook"), blank=True)
    twitter_url = models.URLField(_("Twitter/X"), blank=True)
    instagram_url = models.URLField(_("Instagram"), blank=True)
    linkedin_url = models.URLField(_("LinkedIn"), blank=True)
    youtube_url = models.URLField(_("YouTube"), blank=True)
    
    # Marketing materials
    company_logo = models.ImageField(_("Logo de la empresa"), upload_to="suppliers/logos/", blank=True)
    company_banner = models.ImageField(_("Banner de la empresa"), upload_to="suppliers/banners/", blank=True)
    brochure = models.FileField(_("Brochure/Catálogo"), upload_to="suppliers/brochures/", blank=True)
    
    # Sponsorship preferences
    sponsorship_budget_min = models.PositiveIntegerField(_("Presupuesto mínimo de patrocinio"), blank=True, null=True)
    sponsorship_budget_max = models.PositiveIntegerField(_("Presupuesto máximo de patrocinio"), blank=True, null=True)
    preferred_event_types = models.JSONField(_("Tipos de eventos preferidos"), default=list, blank=True)
    preferred_locations = models.JSONField(_("Ubicaciones preferidas"), default=list, blank=True)
    target_audience = models.TextField(_("Audiencia objetivo"), max_length=500, blank=True)
    
    # Admin review
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="reviewed_supplier_profiles",
        help_text=_("Administrador que revisó la aplicación")
    )
    reviewed_at = models.DateTimeField(_("Fecha de revisión"), null=True, blank=True)
    admin_notes = models.TextField(_("Notas del administrador"), blank=True)
    rejection_reason = models.TextField(_("Razón de rechazo"), blank=True)
    
    # Settings
    is_public = models.BooleanField(_("Perfil público"), default=True)
    allow_contact = models.BooleanField(_("Permitir contacto directo"), default=True)
    email_notifications = models.BooleanField(_("Notificaciones por email"), default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(_("Fecha de aprobación"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Supplier Profile")
        verbose_name_plural = _("Supplier Profiles")
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.company_name} - {self.user.name or self.user.email}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Use company name if available, otherwise use user info
            if self.company_name:
                base_slug = slugify(self.company_name)
            else:
                # Fallback to user name or email
                user_name = self.user.name or self.user.email.split('@')[0]
                base_slug = slugify(f"supplier-{user_name}")
            
            # Ensure we have a valid slug
            if not base_slug:
                base_slug = f"supplier-{self.user.id}"
            
            self.slug = base_slug
            
            # Ensure uniqueness
            counter = 1
            while SupplierProfile.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("users:supplier_profile", kwargs={"slug": self.slug})
    
    @property
    def is_approved(self):
        return self.status == 'approved'
    
    @property
    def sponsored_events_count(self):
        """Count of events this supplier has sponsored."""
        from experienciaas.events.models import EventSponsor
        return EventSponsor.objects.filter(
            sponsor__supplier_profile=self
        ).count()
    
    @property
    def active_applications_count(self):
        """Count of pending sponsorship applications."""
        from experienciaas.events.models import SponsorshipApplication
        return SponsorshipApplication.objects.filter(
            supplier_profile=self,
            status='pending'
        ).count()


class RoleApplication(models.Model):
    """Model for users applying for organizer or supplier roles."""
    ROLE_CHOICES = [
        ('organizer', _('Organizador')),
        ('supplier', _('Proveedor/Patrocinador')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pendiente')),
        ('approved', _('Aprobado')),
        ('rejected', _('Rechazado')),
        ('under_review', _('En revisión')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="role_applications")
    role = models.CharField(_("Rol solicitado"), max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(_("Estado"), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Application details
    motivation = models.TextField(
        _("Motivación"), 
        max_length=1000,
        help_text=_("Explica por qué quieres este rol y cómo planeas usarlo")
    )
    experience = models.TextField(
        _("Experiencia relevante"), 
        max_length=1000, 
        blank=True,
        help_text=_("Describe tu experiencia previa relacionada con este rol")
    )
    additional_info = models.TextField(_("Información adicional"), max_length=500, blank=True)
    
    # Admin review
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="reviewed_role_applications"
    )
    reviewed_at = models.DateTimeField(_("Fecha de revisión"), null=True, blank=True)
    admin_notes = models.TextField(_("Notas del administrador"), blank=True)
    rejection_reason = models.TextField(_("Razón de rechazo"), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Role Application")
        verbose_name_plural = _("Role Applications")
        ordering = ["-created_at"]
        unique_together = [["user", "role", "status"]]  # One pending application per role per user
    
    def __str__(self):
        return f"{self.user.name or self.user.email} - {self.get_role_display()} ({self.get_status_display()})"


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


class SponsorshipApplication(models.Model):
    """Model for supplier sponsorship applications to events."""
    STATUS_CHOICES = [
        ('pending', _('Pendiente')),
        ('approved', _('Aprobado')),
        ('rejected', _('Rechazado')),
        ('under_review', _('En revisión')),
        ('contracted', _('Contratado')),
    ]
    
    TIER_CHOICES = [
        ('platinum', _('Platinum')),
        ('gold', _('Gold')),
        ('silver', _('Silver')),
        ('bronze', _('Bronze')),
        ('partner', _('Partner')),
    ]
    
    # Relations
    supplier_profile = models.ForeignKey(
        SupplierProfile, 
        on_delete=models.CASCADE, 
        related_name="sponsorship_applications"
    )
    event = models.ForeignKey(
        'events.Event', 
        on_delete=models.CASCADE, 
        related_name="supplier_applications"
    )
    
    # Application details
    proposed_tier = models.CharField(_("Nivel de patrocinio propuesto"), max_length=20, choices=TIER_CHOICES)
    budget_offered = models.PositiveIntegerField(_("Presupuesto ofrecido"), blank=True, null=True)
    message = models.TextField(
        _("Mensaje"), 
        max_length=1000,
        help_text=_("Explica por qué quieres patrocinar este evento y qué puedes ofrecer")
    )
    special_requirements = models.TextField(_("Requerimientos especiales"), max_length=500, blank=True)
    
    # Status and review
    status = models.CharField(_("Estado"), max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="reviewed_sponsorship_applications"
    )
    reviewed_at = models.DateTimeField(_("Fecha de revisión"), null=True, blank=True)
    organizer_notes = models.TextField(_("Notas del organizador"), blank=True)
    admin_notes = models.TextField(_("Notas del administrador"), blank=True)
    
    # Contract details (when approved)
    final_tier = models.CharField(_("Nivel final"), max_length=20, choices=TIER_CHOICES, blank=True)
    contract_amount = models.PositiveIntegerField(_("Monto del contrato"), blank=True, null=True)
    contract_notes = models.TextField(_("Notas del contrato"), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Sponsorship Application")
        verbose_name_plural = _("Sponsorship Applications")
        ordering = ["-created_at"]
        unique_together = [["supplier_profile", "event"]]  # One application per supplier per event
    
    def __str__(self):
        return f"{self.supplier_profile.company_name} - {self.event.title} ({self.get_status_display()})"
