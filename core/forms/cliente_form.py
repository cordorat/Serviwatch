from django import forms
from core.models import Cliente

class ClienteForm(forms.ModelForm):
    telefono = forms.CharField(
        label="Teléfono",
        required=True,
        max_length=10,
        min_length=10,
        widget=forms.TextInput(attrs={
            'class': 'validate',
            'placeholder': 'Ingresa el número de teléfono'
        })
    )

    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'validate',
                'placeholder': 'Ingresa el nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'validate',
                'placeholder': 'Ingresa el apellido'
            }),
        }

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')

        if not telefono.isdigit():
            raise forms.ValidationError("El número de teléfono solo debe contener números.")

        if len(telefono) != 10:
            raise forms.ValidationError("El número de teléfono debe tener exactamente 10 dígitos.")

        return telefono