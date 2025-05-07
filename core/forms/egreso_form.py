from django import forms
from core.models.egreso import Egreso
from django.utils import timezone
from datetime import timedelta

class EgresoForm(forms.ModelForm):
    """
    Formulario para gestionar el registro de egresos.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar clases CSS a campos con errores después de la validación
        if self.errors:
            for field in self.fields:
                if field in self.errors:
                     self.fields[field].widget.attrs.update({'class': 'form-control is-invalid'})
                     
    fecha = forms.DateField(
        input_formats=['%d/%m/%Y'],
        required=True,
        widget=forms.DateInput(
            attrs={
                'type': 'text',
                'id': 'id_fecha',
                'class': 'form-control text-secondary',
                'placeholder': 'Fecha',
            }
        )
    )    
    
    class Meta:

        model = Egreso
        fields = ['fecha', 'valor', 'descripcion']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'class': 'form-control text-secondary',
                'type': 'date',
                'placeholder': 'Ingrese la fecha del egreso'
            }), 
            'valor': forms.NumberInput(attrs={
                'class': 'form-control text-secondary',
                'min': '0',
                'step': '1',  # Para enteros, no decimales
                'placeholder': 'Valor'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control text-secondary',
                'rows': 3,
                'placeholder': 'Descripción'
            }),
        }
        error_messages = {

            'fecha': {
                'required': 'La fecha es obligatoria.',
            },
            'valor': {
                'required': 'El valor es obligatorio.',
            },
            'descripcion': {
                'required': 'La descripcion es obligatorio.',
            }            
        }        


        
    def clean_valor(self):
        """
        Valida que el valor sea un número positivo.
        """
        valor = self.cleaned_data.get('valor')
        if valor <= 0:
            raise forms.ValidationError("El valor debe ser mayor que cero")
        return valor
    
    def clean_fecha(self):
        """
        Valida que la fecha no sea en el futuro ni anterior a 7 días desde hoy.
        """
        fecha = self.cleaned_data.get('fecha')
        
        if fecha is None:
            raise forms.ValidationError("La fecha es obligatoria")
        
        hoy = timezone.now().date()
        hace_una_semana = hoy - timedelta(days=7)

        if fecha > hoy:
            raise forms.ValidationError("La fecha no puede ser en el futuro")
        if fecha < hace_una_semana:
            raise forms.ValidationError("La fecha no puede ser anterior a una semana")
        
        return fecha