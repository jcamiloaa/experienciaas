from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Category, City, Event, SponsorshipApplication, Sponsor, EventSponsor, SponsorshipApplication, Sponsor, EventSponsor


class EventForm(forms.ModelForm):
    """Form for creating and editing events."""
    
    class Meta:
        model = Event
        fields = [
            'title', 'short_description', 'description', 'category', 'city',
            'venue_name', 'address', 'latitude', 'longitude',
            'start_date', 'end_date', 'price_type', 'price', 'currency',
            'max_attendees', 'max_sponsors', 'sponsorship_open', 
            'image', 'status', 'is_featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del evento'
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Descripción corta (máximo 300 caracteres)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Descripción completa del evento'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'city': forms.Select(attrs={
                'class': 'form-select'
            }),
            'venue_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del lugar'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Dirección completa'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Latitud (opcional)',
                'step': 'any'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Longitud (opcional)',
                'step': 'any'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'price_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'currency': forms.Select(attrs={
                'class': 'form-select'
            }),
            'max_attendees': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'max_sponsors': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0 = Sin patrocinadores'
            }),
            'sponsorship_open': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter active categories and cities
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        self.fields['city'].queryset = City.objects.filter(is_active=True)
        
        # Make price and currency fields not required initially
        self.fields['price'].required = False
        self.fields['currency'].required = False

    def clean(self):
        cleaned_data = super().clean()
        price_type = cleaned_data.get('price_type')
        price = cleaned_data.get('price')
        currency = cleaned_data.get('currency')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        max_sponsors = cleaned_data.get('max_sponsors')
        sponsorship_open = cleaned_data.get('sponsorship_open')
        
        # Validate price and currency for paid events
        if price_type == 'paid':
            if not price:
                raise forms.ValidationError(_('Price is required for paid events.'))
            if not currency:
                raise forms.ValidationError(_('Currency is required for paid events.'))
        
        # Validate dates
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError(_('End date must be after start date.'))
        
        # Validate sponsor settings
        if sponsorship_open and (max_sponsors is None or max_sponsors <= 0):
            raise forms.ValidationError(_('You must set a maximum number of sponsors greater than 0 if sponsorship applications are open.'))
        
        return cleaned_data

    def save(self, commit=True):
        event = super().save(commit=False)
        if self.user:
            event.organizer = self.user
        
        # Clear price and currency for free events
        if event.price_type == 'free':
            event.price = None
            event.currency = ''
            
        if commit:
            event.save()
        return event


class EventFilterForm(forms.Form):
    """Form for filtering events in admin dashboard."""
    
    STATUS_CHOICES = [('', 'Todos los estados')] + Event.STATUS_CHOICES
    PRICE_TYPE_CHOICES = [('', 'Todos los tipos')] + Event.PRICE_TYPE_CHOICES
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar eventos...'
        })
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label='Todas las categorías',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    city = forms.ModelChoiceField(
        queryset=City.objects.filter(is_active=True),
        required=False,
        empty_label='Todas las ciudades',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    price_type = forms.ChoiceField(
        choices=PRICE_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    is_featured = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class BulkActionForm(forms.Form):
    """Form for bulk actions on events."""
    
    ACTION_CHOICES = [
        ('', 'Seleccionar acción...'),
        ('publish', 'Publicar eventos'),
        ('draft', 'Marcar como borrador'),
        ('feature', 'Marcar como destacados'),
        ('unfeature', 'Quitar de destacados'),
        ('delete', 'Eliminar eventos'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    selected_events = forms.CharField(
        widget=forms.HiddenInput()
    )


class CategoryForm(forms.ModelForm):
    """Form for creating and editing categories."""
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'icon', 'color', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la categoría'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'fas fa-music'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class CityForm(forms.ModelForm):
    """Form for creating and editing cities."""
    
    class Meta:
        model = City
        fields = ['name', 'country', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la ciudad'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'País'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class SponsorshipApplicationForm(forms.ModelForm):
    """Form for applying for event sponsorship."""
    
    # Custom field to remove URL validation
    company_website = forms.CharField(
        label=_('Sitio Web de la Empresa'),
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'www.empresa.com o https://www.empresa.com'
        }),
        help_text=_('Ingresa la URL de tu sitio web (opcional)')
    )
    
    class Meta:
        model = SponsorshipApplication
        fields = [
            'company_name', 'contact_name', 'contact_email', 'contact_phone',
            'company_website', 'message', 'proposed_tier'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la empresa'
            }),
            'contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del contacto'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@empresa.com'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+57 300 123 4567'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe tu empresa y por qué quieres patrocinar este evento...'
            }),
            'proposed_tier': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'company_name': _('Nombre de la Empresa'),
            'contact_name': _('Nombre del Contacto'),
            'contact_email': _('Email de Contacto'),
            'contact_phone': _('Teléfono de Contacto'),
            'message': _('Mensaje'),
            'proposed_tier': _('Nivel de Patrocinio Propuesto')
        }
    
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        
        # Add tier descriptions as help text
        tier_descriptions = {
            'platinum': _('Nivel más alto: Logo prominente, menciones especiales, stand preferencial'),
            'gold': _('Nivel alto: Logo destacado, menciones en redes sociales, buen espacio de stand'),
            'silver': _('Nivel medio: Logo visible, menciones ocasionales, espacio de stand estándar'),
            'bronze': _('Nivel básico: Logo en materiales, menciones básicas, espacio de stand pequeño'),
            'partner': _('Nivel colaborador: Logo en materiales básicos, reconocimiento como colaborador'),
        }
        
        # Update the proposed_tier field with better choices and descriptions
        self.fields['proposed_tier'].choices = [
            ('partner', 'Partner - Colaborador'),
            ('bronze', 'Bronze - Bronce'),
            ('silver', 'Silver - Plata'),
            ('gold', 'Gold - Oro'),
            ('platinum', 'Platinum - Platino'),
        ]
        
        self.fields['proposed_tier'].help_text = _(
            'Selecciona el nivel de patrocinio que mejor se adapte a tu presupuesto y objetivos.'
        )
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.event:
            instance.event = self.event
        if commit:
            instance.save()
        return instance


class SponsorForm(forms.ModelForm):
    """Form for creating/editing sponsors (admin use)."""
    
    # Custom field to remove URL validation
    website = forms.CharField(
        label=_('Sitio Web'),
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'www.empresa.com o https://www.empresa.com'
        }),
        help_text=_('Ingresa la URL del sitio web (opcional)')
    )
    
    class Meta:
        model = Sponsor
        fields = [
            'name', 'logo', 'description', 'website', 'contact_email', 'contact_phone',
            'facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'is_approved'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la empresa'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción de la empresa...'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contacto@empresa.com'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+57 300 123 4567'
            }),
            'facebook_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://facebook.com/empresa'
            }),
            'twitter_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://twitter.com/empresa'
            }),
            'instagram_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://instagram.com/empresa'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/company/empresa'
            }),
            'is_approved': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class EventSponsorForm(forms.ModelForm):
    """Form for linking sponsors to events."""
    
    class Meta:
        model = EventSponsor
        fields = ['sponsor', 'tier', 'custom_description', 'is_featured', 'display_order']
        widgets = {
            'sponsor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tier': forms.Select(attrs={
                'class': 'form-select'
            }),
            'custom_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción personalizada para este evento (opcional)'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        # Only show approved sponsors
        self.fields['sponsor'].queryset = Sponsor.objects.filter(is_approved=True)


class SponsorshipApplicationUpdateForm(forms.ModelForm):
    """Form for updating sponsorship applications (admin use)."""
    
    class Meta:
        model = SponsorshipApplication
        fields = ['status', 'admin_notes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'admin_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Notas internas para el equipo organizador...'
            })
        }
        labels = {
            'status': _('Estado'),
            'admin_notes': _('Notas Administrativas')
        }
