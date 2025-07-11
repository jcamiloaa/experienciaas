from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import gettext_lazy as _

from .models import User


class EmailChangeForm(forms.Form):
    """
    Form for changing user email with password confirmation.
    This should only be used in exceptional cases.
    """
    new_email = forms.EmailField(
        label=_("Nuevo email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('nuevo@email.com')
        }),
        help_text=_("Introduce tu nueva dirección de email")
    )
    
    confirm_email = forms.EmailField(
        label=_("Confirmar nuevo email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('nuevo@email.com')
        }),
        help_text=_("Confirma tu nueva dirección de email")
    )
    
    password = forms.CharField(
        label=_("Contraseña actual"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Tu contraseña actual')
        }),
        help_text=_("Confirma tu contraseña actual para verificar tu identidad")
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_new_email(self):
        email = self.cleaned_data.get('new_email')
        if email:
            # Check if email is different from current
            if email == self.user.email:
                raise forms.ValidationError(_("El nuevo email debe ser diferente al actual"))
            
            # Check if email is already taken
            if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
                raise forms.ValidationError(_("Este email ya está en uso por otro usuario"))
        
        return email
    
    def clean_confirm_email(self):
        new_email = self.cleaned_data.get('new_email')
        confirm_email = self.cleaned_data.get('confirm_email')
        
        if new_email and confirm_email:
            if new_email != confirm_email:
                raise forms.ValidationError(_("Los emails no coinciden"))
        
        return confirm_email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            if not self.user.check_password(password):
                raise forms.ValidationError(_("La contraseña actual es incorrecta"))
        
        return password
    
    def save(self):
        """Save the new email to the user."""
        self.user.email = self.cleaned_data['new_email']
        self.user.save(update_fields=['email'])
        return self.user
