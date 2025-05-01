from django import forms
from core.models import Cliente

class ClienteForm(forms.ModelForm):
    telefono = forms.CharField(
        label="Teléfono",
        required=True,
        max_length=10,
        min_length=10,
        widget=forms.TextInput(attrs={
            'class': 'validate form-control',
            'placeholder': 'Telefono',
        }),
        error_messages={
            'required': 'El número de teléfono es obligatorio.',
            'min_length': 'El número de teléfono debe tener al menos 10 dígitos.',
            'invalid': 'El número de teléfono solo puede contener números.'
        }
    )

    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'validate form-control',
                'placeholder': 'Nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'validate form-control',
                'placeholder': 'Apellido'
            }),
        }
        error_messages = {
            'nombre': {
                'required': 'El nombre es obligatorio.',
                'max_length': 'El nombre no puede tener más de 50 caracteres.',
                'invalid': 'El nombre solo puede contener letras.'
            },
            'apellido': {
                'required': 'El apellido es obligatorio.',
                'max_length': 'El apellido no puede tener más de 50 caracteres.',
                'invalid': 'El apellido solo puede contener letras.'
            }
        }

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')

        if not telefono.isdigit():
            raise forms.ValidationError("El número de teléfono solo debe contener números.")

        if len(telefono) != 10:
            raise forms.ValidationError("El número de teléfono debe tener exactamente 10 dígitos.")

        return telefono
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre.isalpha():
            raise forms.ValidationError("El nombre solo debe contener letras.")
        return nombre
    
    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')
        if not apellido.isalpha():
            raise forms.ValidationError("El apellido solo debe contener letras.")
        return apellido