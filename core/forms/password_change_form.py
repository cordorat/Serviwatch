import re
from django import forms

mensaje_campo_requerido = 'Este campo es obligatorio'
mensaje_tamaño_minimo = 'La contraseña debe tener al menos 8 caracteres'
mensaje_tamaño_maximo = 'La contraseña no puede tener más de 16 caracteres'
contrasenia_nueva_parametro = 'contrasenia_nueva'

class PasswordChangeForm(forms.Form):
    contrasenia_actual = forms.CharField(
        required=True,
        min_length=8,
        max_length=16,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'CONTRASEÑA ACTUAL'
        }),
        error_messages={
            'required': mensaje_campo_requerido,
            'min_length': mensaje_tamaño_minimo,
            'max_length': mensaje_tamaño_maximo,
        }
    )
    contrasenia_nueva = forms.CharField(
        required=True,
        min_length=8,
        max_length=16,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'CONTRASEÑA NUEVA'
        }),
        error_messages={
            'required': mensaje_campo_requerido,
            'min_length': mensaje_tamaño_minimo,
            'max_length': mensaje_tamaño_maximo,
        }
    )
    confirmacion_contrasenia = forms.CharField(
        required=True,
        min_length=8,
        max_length=16,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'CONFIRMAR CONTRASEÑA'
        }),
        error_messages={
            'required': mensaje_campo_requerido,
            'min_length': mensaje_tamaño_minimo,
            'max_length': mensaje_tamaño_maximo,
        }
    )

    def clean_contrasenia_nueva(self):
        contrasenia_nueva = self.cleaned_data.get(contrasenia_nueva_parametro)

        if not re.search(r'[A-Za-z]', contrasenia_nueva):
            raise forms.ValidationError('La contraseña debe tener al menos una letra')
        
        if not re.search(r'\d', contrasenia_nueva):
            raise forms.ValidationError('La contraseña debe tener al menos un número')
        
        if not re.search(r'[!@#$%^&*?]', contrasenia_nueva):
            raise forms.ValidationError('La contraseña debe tener al menos un caracter especial')
        
        return contrasenia_nueva

    def clean_confirmacion_contrasenia(self):
        contrasenia_nueva = self.cleaned_data.get(contrasenia_nueva_parametro)
        confirmacion_contrasenia = self.cleaned_data.get('confirmacion_contraseña')
        
        if contrasenia_nueva and confirmacion_contrasenia and contrasenia_nueva != confirmacion_contrasenia:
            raise forms.ValidationError('Las contraseñas no coinciden')
        
        return confirmacion_contrasenia

    def clean(self):
        cleaned_data = super().clean()
        contrasenia_actual = cleaned_data.get('contrasenia_actual')
        contrasenia_nueva = cleaned_data.get(contrasenia_nueva_parametro)
        
        if contrasenia_actual and contrasenia_nueva and contrasenia_actual == contrasenia_nueva:
            self.add_error(contrasenia_nueva_parametro, 'La contraseña nueva no puede ser igual a la anterior')
        
        return cleaned_data