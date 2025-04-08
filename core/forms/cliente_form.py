from django import forms
from core.models import Cliente
from django.core.validators import EmailValidator
import re


class ClienteForm(forms.ModelForm):
    email = forms.CharField(
        label="Correo electrónico",
        required=True
    )

    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'email', 'telefono']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if '@' not in email or not email.endswith('.com'):
            raise forms.ValidationError(
                "El correo debe tener un formato válido, como nombre@dominio.com"
            )
