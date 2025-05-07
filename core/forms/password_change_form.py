import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

class PasswordChangeForm(forms.Form):
    """
    Formulario para cambiar la contraseña del usuario.
    """

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Aplicar clases CSS a campos con errores después de la validación
        if self.errors:
            for field in self.fields:
                if field in self.errors:
                    self.fields[field].widget.attrs.update({'class': 'form-control is-invalid'})
    
    contraseña_actual = forms.CharField(
        required=True,
        min_length=8,
        max_length=16,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'CONTRASEÑA ACTUAL',
            'autocomplete': 'current-password'
        }),
        error_messages={
            'required': 'Este campo es obligatorio',
            'min_length': 'La contraseña debe tener al menos 8 caracteres',
            'max_length': 'La contraseña no puede tener más de 16 caracteres',
        }
    )
    
    contraseña_nueva = forms.CharField(
        required=True,
        min_length=8,
        max_length=16,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'CONTRASEÑA NUEVA',
            'autocomplete': 'new-password'
        }),
        error_messages={
            'required': 'Este campo es obligatorio',
            'min_length': 'La contraseña debe tener al menos 8 caracteres',
            'max_length': 'La contraseña no puede tener más de 16 caracteres',
        }
    )
    
    confirmacion_contraseña = forms.CharField(
        required=True,
        min_length=8,
        max_length=16,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'CONFIRMAR CONTRASEÑA',
            'autocomplete': 'new-password'
        }),
        error_messages={
            'required': 'Este campo es obligatorio',
            'min_length': 'La contraseña debe tener al menos 8 caracteres',
            'max_length': 'La contraseña no puede tener más de 16 caracteres',
        }
    )

    def clean_contraseña_actual(self):
        """
        Verifica que la contraseña actual sea correcta.
        """
        contraseña_actual = self.cleaned_data.get('contraseña_actual')
        
        if self.user and not self.user.check_password(contraseña_actual):
            raise forms.ValidationError('La contraseña actual es incorrecta')
            
        return contraseña_actual

    def clean_contraseña_nueva(self):
        """
        Valida que la nueva contraseña cumpla con los requisitos de seguridad.
        """
        contraseña_nueva = self.cleaned_data.get('contraseña_nueva')
        
        if contraseña_nueva is None:
            return contraseña_nueva  # El error required ya está manejado
        
        if not re.search(r'[A-Za-z]', contraseña_nueva):
            raise forms.ValidationError('La contraseña debe tener al menos una letra')
        
        if not re.search(r'\d', contraseña_nueva):
            raise forms.ValidationError('La contraseña debe tener al menos un número')
        
        if not re.search(r'[!@#$%^&*?]', contraseña_nueva):
            raise forms.ValidationError('La contraseña debe tener al menos un caracter especial')
        
        return contraseña_nueva

    def clean_confirmacion_contraseña(self):
        """
        Verifica que las contraseñas coincidan.
        """
        contraseña_nueva = self.cleaned_data.get('contraseña_nueva')
        confirmacion_contraseña = self.cleaned_data.get('confirmacion_contraseña')
        
        if contraseña_nueva and confirmacion_contraseña and contraseña_nueva != confirmacion_contraseña:
            raise forms.ValidationError('Las contraseñas no coinciden')
        
        return confirmacion_contraseña

    def clean(self):
        """
        Validaciones adicionales que dependen de múltiples campos.
        """
        cleaned_data = super().clean()
        contraseña_actual = cleaned_data.get('contraseña_actual')
        contraseña_nueva = cleaned_data.get('contraseña_nueva')
        
        if contraseña_actual and contraseña_nueva and contraseña_actual == contraseña_nueva:
            self.add_error('contraseña_nueva', 'La contraseña nueva no puede ser igual a la anterior')
        
        return cleaned_data
        
    def save(self, commit=True):
        """
        Guarda la nueva contraseña para el usuario.
        """
        if self.user and commit:
            self.user.set_password(self.cleaned_data.get('contraseña_nueva'))
            self.user.save()
        return self.user