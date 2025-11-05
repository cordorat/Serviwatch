from django import forms
from core.models.abono import Abono

class AbonoForm(forms.Form):  # Changed to Form instead of ModelForm
    monto = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Monto del abono',
        }),
        error_messages={
            'required': 'El monto es obligatorio'
        }
    )
    
    descripcion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Descripción (opcional)'
        })
    )

    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        try:
            monto_int = int(monto)
            if monto_int <= 0:
                raise forms.ValidationError("El monto debe ser mayor a 0")
            return str(monto_int)
        except (ValueError, TypeError):
            raise forms.ValidationError("El monto debe ser un número válido")

    def save(self, reloj):
        # Create abono instance manually
        return Abono.objects.create(
            reloj=reloj,
            monto=self.cleaned_data['monto'],
            descripcion=self.cleaned_data.get('descripcion', '')
        )