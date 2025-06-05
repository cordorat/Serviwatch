from django import forms
from core.models.abono import Abono

class AbonoForm(forms.ModelForm):
    monto = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Monto del abono'
        })
    )
    
    descripcion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Descripción (opcional)'
        })
    )

    class Meta:
        model = Abono
        fields = ['monto', 'descripcion']

    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        try:
            monto_int = int(monto)
            if monto_int <= 0:
                raise forms.ValidationError("El monto debe ser mayor a 0")
        except ValueError:
            raise forms.ValidationError("El monto debe ser un número válido")
        return monto