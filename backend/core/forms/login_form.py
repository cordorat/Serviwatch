import re
from django import forms

class LoginForm(forms.Form):
    usuario = forms.CharField(
        required=True,
        min_length=8,
        max_length=16,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'USUARIO'
        }),
        error_messages={
            'required': 'Ingrese las credenciales',
            'min_length': 'El usuario debe tener al menos 8 caracteres',
            'max_length': 'El usuario no puede tener más de 16 caracteres',
        }
    )
    contrasenia = forms.CharField(
        required=True,
        min_length=8,
        max_length=16,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'CONTRASEÑA'
        }),
        error_messages={
            'required': 'Ingrese las credenciales',
            'min_length': 'La contraseña debe tener al menos 8 caracteres',
            'max_length': 'La contraseña no puede tener más de 16 caracteres',
        }
    )

    def clean_usuario(self):
        usuario = self.cleaned_data.get('usuario')
        if not usuario.isalpha():
            raise forms.ValidationError('El usuario debe contener solo letras.')
        return usuario

    def clean_contrasenia(self):
        contrasenia = self.cleaned_data.get('contrasenia')

        if not re.search(r'[A-Za-z]', contrasenia):
            raise forms.ValidationError('La contraseña debe tener al menos una letra')
        
        if not re.search(r'\d', contrasenia):
            raise forms.ValidationError('La contraseña debe tener al menos un numero')
        
        if not re.search(r'[!@#$%^&*?]', contrasenia):
            raise forms.ValidationError('La contraseña debe tener al menos un caracter especial')
        
        return contrasenia
    
    