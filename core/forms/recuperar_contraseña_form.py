import re
from django import forms

class recuperarContrasenaForm(forms.Form):
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