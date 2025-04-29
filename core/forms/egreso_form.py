from django import forms
from core.models import Egreso

class EgresoForm(forms.ModelForm):
    class Meta:
        model = Egreso
        fields = ['valor', 'fecha', 'descripcion']
        widgets = {
            'fecha': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'aria-label': 'Fecha del egreso',
                    'placeholder':'FECHA'
                },
                format='%d/%m/%Y'
            ),'valor': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'aria-label': 'Valor del egreso',
                    'placeholder':'VALOR'
                }
            ),
            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'aria-label': 'Descripción del egreso',
                    'placeholder':'DESCRIPCION'
                }
            )
        }
        error_messages = {
            'fecha': {
                'required': 'Campo incompleto',
                'invalid': 'Ingrese una fecha válida'
            },
            'valor': {
                'required': 'Campo incompleto',
                'invalid': 'Ingrese un número válido',
                'max_digits':'Valor demasiado grande. Límite máximo de 10 números'
            },
            'descripcion': {
                'required': 'Campo incompleto',
                'invalid': 'Ingrese un texto válido',
                'max_length':'Descripción demasiado larga'
            }
        }
    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if len(descripcion) > 100:
            raise forms.ValidationError("Máximo 100 caracteres permitidos")
        return descripcion

