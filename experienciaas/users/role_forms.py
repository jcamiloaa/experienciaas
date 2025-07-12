from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .models import RoleApplication, SupplierProfile, OrganizerProfile


class RoleApplicationForm(forms.ModelForm):
    """Base form for role applications."""
    
    class Meta:
        model = RoleApplication
        fields = ['role', 'motivation', 'experience', 'additional_info']
        widgets = {
            'role': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'motivation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': _('Explica por qué quieres este rol y cómo planeas usarlo...'),
                'required': True
            }),
            'experience': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Describe tu experiencia previa relacionada con este rol...')
            }),
            'additional_info': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Información adicional que consideres relevante...')
            }),
        }
        labels = {
            'role': _('Rol solicitado'),
            'motivation': _('Motivación'),
            'experience': _('Experiencia relevante'),
            'additional_info': _('Información adicional'),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter available roles based on user's current status
        available_roles = []
        
        if self.user:
            if self.user.can_apply_for_organizer:
                available_roles.append(('organizer', _('Organizador')))
            if self.user.can_apply_for_supplier:
                available_roles.append(('supplier', _('Proveedor/Patrocinador')))
        
        self.fields['role'].choices = available_roles
        
        if not available_roles:
            self.fields['role'].widget = forms.HiddenInput()
            self.fields['role'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        
        if not self.user:
            raise ValidationError(_('Usuario requerido'))
        
        # Check if user can apply for this role
        if role == 'organizer' and not self.user.can_apply_for_organizer:
            raise ValidationError(_('No puedes aplicar para el rol de organizador en este momento'))
        
        if role == 'supplier' and not self.user.can_apply_for_supplier:
            raise ValidationError(_('No puedes aplicar para el rol de proveedor en este momento'))
        
        # Check for existing pending applications
        existing = RoleApplication.objects.filter(
            user=self.user,
            role=role,
            status='pending'
        ).exists()
        
        if existing:
            raise ValidationError(_('Ya tienes una aplicación pendiente para este rol'))
        
        return cleaned_data


class OrganizerApplicationForm(RoleApplicationForm):
    """Specific form for organizer applications."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].initial = 'organizer'
        self.fields['role'].widget = forms.HiddenInput()
        
        # Add specific help texts for organizer role
        self.fields['motivation'].help_text = _(
            'Explica por qué quieres organizar eventos en nuestra plataforma y qué tipo de eventos planeas crear.'
        )
        self.fields['experience'].help_text = _(
            'Describe tu experiencia previa organizando eventos, gestionando proyectos, o trabajando en áreas relacionadas.'
        )


class SupplierApplicationForm(RoleApplicationForm):
    """Specific form for supplier applications."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].initial = 'supplier'
        self.fields['role'].widget = forms.HiddenInput()
        
        # Add specific help texts for supplier role
        self.fields['motivation'].help_text = _(
            'Explica por qué quieres ser un proveedor/patrocinador en nuestra plataforma y qué puedes ofrecer.'
        )
        self.fields['experience'].help_text = _(
            'Describe tu experiencia en marketing, patrocinios, o colaboraciones con eventos.'
        )


class SupplierProfileForm(forms.ModelForm):
    """Form for creating/editing supplier profiles."""
    
    class Meta:
        model = SupplierProfile
        fields = [
            'company_name', 'company_description', 'company_size', 'industry', 
            'founding_year', 'tax_id', 'legal_address', 'business_phone', 
            'business_email', 'contact_person', 'contact_position', 'company_website',
            'facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'youtube_url',
            'company_logo', 'company_banner', 'brochure', 'sponsorship_budget_min',
            'sponsorship_budget_max', 'preferred_event_types', 'preferred_locations',
            'target_audience', 'is_public', 'allow_contact', 'email_notifications'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Nombre de tu empresa')
            }),
            'company_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Describe tu empresa, productos y servicios...')
            }),
            'company_size': forms.Select(attrs={'class': 'form-select'}),
            'industry': forms.Select(attrs={'class': 'form-select'}),
            'founding_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1900,
                'max': 2025
            }),
            'tax_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('NIT o RUT de la empresa')
            }),
            'legal_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Dirección legal de la empresa')
            }),
            'business_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Teléfono principal de la empresa')
            }),
            'business_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Email principal de la empresa')
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Nombre de la persona de contacto')
            }),
            'contact_position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Cargo de la persona de contacto')
            }),
            'company_website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://tuempresa.com'
            }),
            'facebook_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://facebook.com/tuempresa'
            }),
            'twitter_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://twitter.com/tuempresa'
            }),
            'instagram_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://instagram.com/tuempresa'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/company/tuempresa'
            }),
            'youtube_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/tuempresa'
            }),
            'company_logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'company_banner': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'brochure': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.ppt,.pptx'
            }),
            'sponsorship_budget_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': _('Presupuesto mínimo en COP')
            }),
            'sponsorship_budget_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': _('Presupuesto máximo en COP')
            }),
            'target_audience': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Describe tu audiencia objetivo...')
            }),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_contact': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help texts
        self.fields['company_logo'].help_text = _('Logo de la empresa (recomendado: 300x300px, PNG o JPG)')
        self.fields['company_banner'].help_text = _('Banner para eventos (recomendado: 1200x400px, PNG o JPG)')
        self.fields['brochure'].help_text = _('Catálogo o brochure de productos/servicios (PDF, DOC, PPT)')
        self.fields['sponsorship_budget_min'].help_text = _('Presupuesto mínimo que puedes destinar a patrocinios')
        self.fields['sponsorship_budget_max'].help_text = _('Presupuesto máximo que puedes destinar a patrocinios')
    
    def clean(self):
        cleaned_data = super().clean()
        budget_min = cleaned_data.get('sponsorship_budget_min')
        budget_max = cleaned_data.get('sponsorship_budget_max')
        
        if budget_min and budget_max and budget_min > budget_max:
            raise ValidationError(_('El presupuesto mínimo no puede ser mayor que el máximo'))
        
        return cleaned_data


class OrganizerProfileForm(forms.ModelForm):
    """Form for creating/editing organizer profiles."""
    
    class Meta:
        model = OrganizerProfile
        fields = [
            'bio', 'website', 'phone', 'location', 'facebook_url', 
            'twitter_url', 'instagram_url', 'linkedin_url', 'avatar', 
            'cover_image', 'is_public', 'allow_contact'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': _('Cuéntanos sobre ti como organizador de eventos...')
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://tusitioweb.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Teléfono de contacto')
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Ciudad, País')
            }),
            'facebook_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://facebook.com/tu-perfil'
            }),
            'twitter_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://twitter.com/tu-perfil'
            }),
            'instagram_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://instagram.com/tu-perfil'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/tu-perfil'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_contact': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help texts
        self.fields['avatar'].help_text = _('Foto de perfil (recomendado: 400x400px)')
        self.fields['cover_image'].help_text = _('Imagen de portada (recomendado: 1200x400px)')
        self.fields['bio'].help_text = _('Máximo 1000 caracteres')


class SponsorshipApplicationForm(forms.ModelForm):
    """Form for suppliers to apply for event sponsorship."""
    
    class Meta:
        model = SupplierProfile  # We'll use SponsorshipApplication when we update events models
        fields = []  # Will be implemented when we update the events models
    
    # This will be implemented in the next phase when we update the events models
    pass
