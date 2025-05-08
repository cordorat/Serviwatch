import re
from django import forms

class PasswordChangeForm(forms.Form):
    contraseña_actual = forms.CharField(
        required=True,
        min_length=8,
        max_length=16,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'CONTRASEÑA ACTUAL'
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
            'placeholder': 'CONTRASEÑA NUEVA'
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
            'placeholder': 'CONFIRMAR CONTRASEÑA'
        }),
        error_messages={
            'required': 'Este campo es obligatorio',
            'min_length': 'La contraseña debe tener al menos 8 caracteres',
            'max_length': 'La contraseña no puede tener más de 16 caracteres',
        }
    )

    def clean_contraseña_nueva(self):
        contraseña_nueva = self.cleaned_data.get('contraseña_nueva')

        if not re.search(r'[A-Za-z]', contraseña_nueva):
            raise forms.ValidationError('La contraseña debe tener al menos una letra')
        
        if not re.search(r'\d', contraseña_nueva):
            raise forms.ValidationError('La contraseña debe tener al menos un número')
        
        if not re.search(r'[!@#$%^&*?]', contraseña_nueva):
            raise forms.ValidationError('La contraseña debe tener al menos un caracter especial')
        
        return contraseña_nueva

    def clean_confirmacion_contraseña(self):
        contraseña_nueva = self.cleaned_data.get('contraseña_nueva')
        confirmacion_contraseña = self.cleaned_data.get('confirmacion_contraseña')
        
        if contraseña_nueva and confirmacion_contraseña and contraseña_nueva != confirmacion_contraseña:
            raise forms.ValidationError('Las contraseñas no coinciden')
        
        return confirmacion_contraseña

    def clean(self):
        cleaned_data = super().clean()
        contraseña_actual = cleaned_data.get('contraseña_actual')
        contraseña_nueva = cleaned_data.get('contraseña_nueva')
        
        if contraseña_actual and contraseña_nueva and contraseña_actual == contraseña_nueva:
            self.add_error('contraseña_nueva', 'La contraseña nueva no puede ser igual a la anterior')
        
        return cleaned_data