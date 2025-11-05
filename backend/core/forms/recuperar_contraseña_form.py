import re
from django import forms

mensaje_tamaño_contraseña = 'La contraseña debe tener entre 8 y 20 caracteres'

class RecuperarContrasenaForm(forms.Form):
    usuario = forms.CharField(
        required = True,
        max_length=20,
        min_length=8,
        widget =forms.TextInput(attrs={
            'placeholder': 'USUARIO'
        }),
        error_messages={
            'required': 'ingrese las credenciales',
            'min_length': 'El usuario debe tener entre 8 y 20 caracteres',
            'max_length': 'El usuario debe tener entre 8 y 20 caracteres',
        }
    )
    email = forms.CharField(
        required= True,
        widget=forms.TextInput(attrs={
            'placeholder': 'EMAIL'
        })
    )

    def clean_usuario(self):
        usuario = self.cleaned_data.get('usuario')
        if not usuario.isalpha():
            raise forms.ValidationError('El usuario debe contener solo letras.')
        return usuario

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not re.search(r'@', email):
            raise forms.ValidationError('Debe cumplir con el formato abc@nnn.com/.co')

        if not (email.endswith('.com') or email.endswith('.co')):
            raise forms.ValidationError('Debe cumplir con el formato abc@nnn.com/.co')
        return email


class CambiarContrasenaForm(forms.Form):
    password = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'NUEVA CONTRASEÑA'
        }),
        min_length=8,
        max_length=20,
        required=True,
        error_messages={
            'required': 'ingrese una contraseña',
            'min_length': mensaje_tamaño_contraseña,
            'max_length': mensaje_tamaño_contraseña,
        }
    )
    confirm_password = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'CONFIRMAR CONTRASEÑA'
        }),
        min_length=8,
        max_length=20,
        required=True,
        error_messages={
            'required': 'Confirme su contraseña',
            'min_length': mensaje_tamaño_contraseña,
            'max_length': mensaje_tamaño_contraseña,
        }
    )
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'\d', password):
            raise forms.ValidationError('La contraseña debe contener al menos un número')
        if not re.search(r'[\W_]', password):
            raise forms.ValidationError('La contraseña debe contener al menos un carácter especial')
        return password
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Las contraseñas no coinciden')
            
        return cleaned_data

