from allauth.account.forms import SignupForm, LoginForm, ResetPasswordForm, ResetPasswordKeyForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth import forms as admin_forms
from django.forms import EmailField
from django.utils.translation import gettext_lazy as _
from django import forms

from .models import User, INTEREST_CHOICES


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.update({
            'placeholder': 'Email',
            'class': 'form-control'
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Contraseña',
            'class': 'form-control'
        })
        self.fields['password'].label = 'Contraseña'
        self.fields['remember'].label = 'Recordarme'


class CustomResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Tu dirección de email',
            'class': 'form-control'
        })
        self.fields['email'].label = 'Dirección de email'


class CustomResetPasswordKeyForm(ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Nueva contraseña',
            'class': 'form-control'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirmar nueva contraseña',
            'class': 'form-control'
        })
        self.fields['password1'].label = 'Nueva Contraseña'
        self.fields['password2'].label = 'Confirmar Nueva Contraseña'


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):  # type: ignore[name-defined]
        model = User
        field_classes = {"email": EmailField}


class UserAdminCreationForm(admin_forms.AdminUserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForms.
    """

    class Meta(admin_forms.UserCreationForm.Meta):  # type: ignore[name-defined]
        model = User
        fields = ("email",)
        field_classes = {"email": EmailField}
        error_messages = {
            "email": {"unique": _("This email has already been taken.")},
        }


class UserUpdateForm(forms.ModelForm):
    """
    Form for updating user profile information.
    """
    interests = forms.MultipleChoiceField(
        choices=INTEREST_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        label=_("Intereses"),
        help_text=_("Selecciona tus áreas de interés (puedes seleccionar varias)")
    )
    
    class Meta:
        model = User
        fields = [
            'name', 'birth_date', 'gender', 'bio',
            'country_code', 'phone_number', 'country', 'city', 
            'address', 'postal_code', 'occupation', 'company', 
            'website', 'linkedin_url', 'twitter_url', 'instagram_url', 
            'facebook_url', 'interests', 'hobbies', 'avatar',
            'profile_visible', 'show_email', 'show_phone',
            'email_notifications', 'sms_notifications', 'marketing_emails'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Tu nombre completo')
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Cuéntanos un poco sobre ti...')
            }),
            'country_code': forms.Select(attrs={
                'class': 'form-select'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('3001234567')
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Colombia')
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Bogotá')
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Calle 123 #45-67')
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('110111')
            }),
            'occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Desarrollador de Software')
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Mi Empresa')
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': _('https://misitio.com')
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': _('https://linkedin.com/in/tuusuario')
            }),
            'twitter_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': _('https://twitter.com/tuusuario')
            }),
            'instagram_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': _('https://instagram.com/tuusuario')
            }),
            'facebook_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': _('https://facebook.com/tuusuario')
            }),
            'hobbies': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': _('Lectura, deportes, música...')
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'profile_visible': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'show_email': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'show_phone': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'sms_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'marketing_emails': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Convert interests from JSON to list for the form
        if self.instance and self.instance.interests:
            self.fields['interests'].initial = self.instance.interests
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Ensure email cannot be changed
        if self.instance.pk:  # Existing user
            user.email = self.instance.email
        
        # Convert interests list to JSON
        interests = self.cleaned_data.get('interests', [])
        user.interests = list(interests) if interests else []
        
        if commit:
            user.save()
        return user


class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """
    name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Tu nombre completo'),
            'class': 'form-control'
        }),
        label=_("Nombre completo")
    )

    def save(self, request):
        user = super().save(request)
        user.name = self.cleaned_data['name']
        user.save()
        return user


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """
    name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': _('Tu nombre completo'),
            'class': 'form-control'
        }),
        label=_("Nombre completo")
    )

    def save(self, request):
        user = super().save(request)
        user.name = self.cleaned_data['name']
        user.save()
        return user


class SupplierProfileUpdateForm(forms.ModelForm):
    """
    Form for updating supplier profile information.
    """
    preferred_event_types = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ejemplo: Conferencias, Talleres, Networking, Ferias comerciales'
        }),
        required=False,
        label=_("Tipos de eventos preferidos"),
        help_text=_("Tipos de eventos que te interesan patrocinar (separados por comas)")
    )
    
    preferred_locations = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ejemplo: Bogotá, Medellín, Cali, Todo Colombia'
        }),
        required=False,
        label=_("Ubicaciones preferidas"),
        help_text=_("Ciudades o regiones donde prefieres patrocinar eventos (separadas por comas)")
    )
    
    class Meta:
        from .models import SupplierProfile
        model = SupplierProfile
        fields = [
            'company_name', 'company_description', 'company_size', 'industry', 'founding_year',
            'tax_id', 'legal_address', 'business_phone', 'business_email', 
            'contact_person', 'contact_position', 'company_website',
            'facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'youtube_url',
            'company_logo', 'company_banner', 'brochure',
            'sponsorship_budget_min', 'sponsorship_budget_max', 'preferred_event_types', 
            'preferred_locations', 'target_audience',
            'is_public', 'allow_contact', 'email_notifications'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'company_size': forms.Select(attrs={'class': 'form-select'}),
            'industry': forms.Select(attrs={'class': 'form-select'}),
            'founding_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1800, 'max': 2025}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'legal_address': forms.TextInput(attrs={'class': 'form-control'}),
            'business_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'business_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_position': forms.TextInput(attrs={'class': 'form-control'}),
            'company_website': forms.URLInput(attrs={'class': 'form-control'}),
            'facebook_url': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter_url': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control'}),
            'youtube_url': forms.URLInput(attrs={'class': 'form-control'}),
            'company_logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'company_banner': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'brochure': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'sponsorship_budget_min': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'sponsorship_budget_max': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'target_audience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_contact': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Convert JSON fields to comma-separated strings for display
        if self.instance and self.instance.pk:
            if self.instance.preferred_event_types:
                if isinstance(self.instance.preferred_event_types, list):
                    self.fields['preferred_event_types'].initial = ', '.join(self.instance.preferred_event_types)
                else:
                    self.fields['preferred_event_types'].initial = self.instance.preferred_event_types
            
            if self.instance.preferred_locations:
                if isinstance(self.instance.preferred_locations, list):
                    self.fields['preferred_locations'].initial = ', '.join(self.instance.preferred_locations)
                else:
                    self.fields['preferred_locations'].initial = self.instance.preferred_locations
    
    def clean_preferred_event_types(self):
        """Convert comma-separated string to list for JSON field."""
        value = self.cleaned_data.get('preferred_event_types', '')
        if value:
            return [item.strip() for item in value.split(',') if item.strip()]
        return []
    
    def clean_preferred_locations(self):
        """Convert comma-separated string to list for JSON field."""
        value = self.cleaned_data.get('preferred_locations', '')
        if value:
            return [item.strip() for item in value.split(',') if item.strip()]
        return []
