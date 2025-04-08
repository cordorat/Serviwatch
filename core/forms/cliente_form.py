from django import forms
from core.models import Cliente

class ClienteForm(forms.ModelForm):
    telefono = forms.CharField(
        label="Teléfono",
        required=True,
        max_length=10,
        min_length=10
    )

    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'telefono']

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')

        if not telefono.isdigit():
            raise forms.ValidationError("El número de teléfono solo debe contener números.")

        if len(telefono) != 10:
            raise forms.ValidationError("El número de teléfono debe tener exactamente 10 dígitos.")

        return telefono