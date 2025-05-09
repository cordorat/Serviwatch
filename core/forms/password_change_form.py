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
    
    contrasenia_actual = forms.CharField(
        required=True,
        min_length=8,
        max_length=16,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña ACTUAL',
            'autocomplete': 'current-password'
        }),
        error_messages={
            'required': 'Este campo es obligatorio',
            'min_length': 'La contraseña debe tener al menos 8 caracteres',
            'max_length': 'La contraseña no puede tener más de 16 caracteres',
        }
    )
    
    contrasenia_nueva = forms.CharField(
        required=True,
        min_length=8,
        max_length=16,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña NUEVA',
            'autocomplete': 'new-password'
        }),
        error_messages={
            'required': 'Este campo es obligatorio',
            'min_length': 'La contraseña debe tener al menos 8 caracteres',
            'max_length': 'La contraseña no puede tener más de 16 caracteres',
        }
    )
    
    confirmacion_contrasenia = forms.CharField(
        required=True,
        min_length=8,
        max_length=16,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'CONFIRMAR contraseña',
            'autocomplete': 'new-password'
        }),
        error_messages={
            'required': 'Este campo es obligatorio',
            'min_length': 'La contraseña debe tener al menos 8 caracteres',
            'max_length': 'La contraseña no puede tener más de 16 caracteres',
        }
    )

    def clean_contrasenia_actual(self):
        """
        Verifica que la contraseña actual sea correcta.
        """
        contrasenia_actual = self.cleaned_data.get('contrasenia_actual')
        
        if self.user and not self.user.check_password(contrasenia_actual):
            raise forms.ValidationError('Contraseña incorrecta')
            
        return contrasenia_actual

    def clean_contrasenia_nueva(self):
        """
        Valida que la nueva contraseña cumpla con los requisitos de seguridad.
        """
        contrasenia_nueva = self.cleaned_data.get('contrasenia_nueva')
        
        if contrasenia_nueva is None:
            return contrasenia_nueva  # El error required ya está manejado
        
        if not re.search(r'[A-Za-z]', contrasenia_nueva):
            raise forms.ValidationError('La contraseña debe tener al menos una letra')
        
        if not re.search(r'\d', contrasenia_nueva):
            raise forms.ValidationError('La contraseña debe tener al menos un número')
        
        if not re.search(r'[!@#$%^&*?]', contrasenia_nueva):
            raise forms.ValidationError('La contraseña debe tener al menos un caracter especial')
        
        return contrasenia_nueva

    def clean_confirmacion_contrasenia(self):
        """
        Verifica que las contraseñas coincidan.
        """
        contrasenia_nueva = self.cleaned_data.get('contrasenia_nueva')
        confirmacion_contrasenia = self.cleaned_data.get('confirmacion_contrasenia')
        
        if contrasenia_nueva and confirmacion_contrasenia and contrasenia_nueva != confirmacion_contrasenia:
            raise forms.ValidationError('Las contraseñas no coinciden')
        
        return confirmacion_contrasenia

    def clean(self):
        """
        Validaciones adicionales que dependen de múltiples campos.
        """
        cleaned_data = super().clean()
        contrasenia_actual = cleaned_data.get('contrasenia_actual')
        contrasenia_nueva = cleaned_data.get('contrasenia_nueva')
        
        if contrasenia_actual and contrasenia_nueva and contrasenia_actual == contrasenia_nueva:
            self.add_error('contrasenia_nueva', 'La contraseña nueva no puede ser igual a la anterior')
        
        return cleaned_data
        
    def save(self, commit=True):
        """
        Guarda la nueva contraseña para el usuario.
        """
        if self.user and commit:
            self.user.set_password(self.cleaned_data.get('contrasenia_nueva'))
            self.user.save()
            return 'Su contraseña ha sido actualizada correctamente'
        return self.user