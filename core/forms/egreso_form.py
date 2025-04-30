from django import forms
from django.core.validators import MaxValueValidator
from core.models.egreso import Egreso
from datetime import date

class EgresoForm(forms.ModelForm):
    class Meta:
        model = Egreso
        fields = ['valor', 'fecha', 'descripcion']
        widgets = {
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el valor'
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'dd/mm/aaaa'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ingrese una descripción'
            })
        }
        error_messages = {
            'valor': {
                'required': 'Campo incompleto',
                'max_digits': 'Valor demasiado grande. Límite máximo de 10 números'
            },
            'fecha': {
                'required': 'Fecha incompleta',
                'invalid': 'Formato de fecha inválido'
            },
            'descripcion': {
                'required': 'Campo incompleto',
                'max_length': 'Descripción demasiado larga'
            }
        }

    def clean_valor(self):
        valor = self.cleaned_data.get('valor')
        if valor is None:
            raise forms.ValidationError('Campo incompleto')
            
        # Añadido: Validación para rechazar valores negativos
        if valor <= 0:
            raise forms.ValidationError('El valor debe ser mayor a cero')
            
        if len(str(int(valor))) > 10:
            raise forms.ValidationError('Valor demasiado grande. Límite máximo de 10 números')
        return valor

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if not descripcion:
            raise forms.ValidationError('Campo incompleto')
        if len(descripcion) > 100:
            raise forms.ValidationError('Descripción demasiado larga')
        return descripcion