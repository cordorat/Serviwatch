import re
from django import forms

class PasswordChangeForm(forms.Form):
    contraseña_actual = forms.CharField(
        required=False,
        min_length=8,
        max_length=16,
        widget=forms.PasswordInput(attrs={
            'id': 'id_contraseña_actual',
            'class': 'form-control',
            'placeholder': 'CONTRASEÑA ACTUAL'
        }),
        error_messages={
            'min_length': 'La contraseña debe tener al menos 8 caracteres',
            'max_length': 'La contraseña no puede tener más de 16 caracteres',
        }
    )
    contraseña_nueva = forms.CharField(
        required=False,
        min_length=8,
        max_length=16,
        widget=forms.PasswordInput(attrs={
            'id': 'id_contraseña_nueva',
            'class': 'form-control',
            'placeholder': 'CONTRASEÑA NUEVA'
        }),
        error_messages={
            'min_length': 'La contraseña debe tener al menos 8 caracteres',
            'max_length': 'La contraseña no puede tener más de 16 caracteres',
        }
    )
    confirmacion_contraseña = forms.CharField(
        required=False,
        min_length=8,
        max_length=16,
        widget=forms.PasswordInput(attrs={
            'id': 'id_confirmacion_contraseña',
            'class': 'form-control',
            'placeholder': 'CONFIRMAR CONTRASEÑA'
        }),
        error_messages={
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
    
    def clean_contraseña_actual(self):
        contraseña_actual = self.cleaned_data.get('contraseña_actual')
        
        if not contraseña_actual:
            raise forms.ValidationError('La contraseña actual es obligatoriaaaa')
            
        if len(contraseña_actual) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres')
            
        if len(contraseña_actual) > 16:
            raise forms.ValidationError('La contraseña no puede tener más de 16 caracteres')
            
        return contraseña_actual

    def clean_confirmacion_contraseña(self):
        confirmacion_contraseña = self.cleaned_data.get('confirmacion_contraseña')
        
        # Validación requerido
        if not confirmacion_contraseña:
            raise forms.ValidationError('La confirmación de contraseña es obligatoria')
            
        # Validaciones de longitud
        if len(confirmacion_contraseña) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres')
        if len(confirmacion_contraseña) > 16:
            raise forms.ValidationError('La contraseña no puede tener más de 16 caracteres')
        
        # Validaciones de caracteres
        if not re.search(r'[A-Za-z]', confirmacion_contraseña):
            raise forms.ValidationError('La contraseña debe tener al menos una letra')
        if not re.search(r'\d', confirmacion_contraseña):
            raise forms.ValidationError('La contraseña debe tener al menos un número')
        if not re.search(r'[!@#$%^&*?]', confirmacion_contraseña):
            raise forms.ValidationError('La contraseña debe tener al menos un caracter especial')
        
        # Validación de coincidencia
        contraseña_nueva = self.cleaned_data.get('contraseña_nueva')
        if contraseña_nueva and confirmacion_contraseña != contraseña_nueva:
            raise forms.ValidationError('Las contraseñas no coinciden')
        
        return confirmacion_contraseña


    def clean(self):
        cleaned_data = super().clean()
        contraseña_actual = cleaned_data.get('contraseña_actual')
        contraseña_nueva = cleaned_data.get('contraseña_nueva')
        
        if contraseña_actual and contraseña_nueva and contraseña_actual == contraseña_nueva:
            self.add_error('contraseña_nueva', 'La contraseña nueva no puede ser igual a la anterior')
        
        return cleaned_data