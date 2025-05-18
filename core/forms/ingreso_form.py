from django import forms
from core.models.ingreso import Ingreso
from django.utils import timezone
from datetime import timedelta
from datetime import date

clase_formulario = 'form-control text-secondary'

class IngresoForm(forms.ModelForm):
    """
    Formulario para gestionar el registro de ingresos.
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
                'class': clase_formulario,
                'placeholder': 'Fecha',
            }
        )
    )    
    
    class Meta:

        model = Ingreso
        fields = ['fecha', 'valor', 'descripcion']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'class': clase_formulario,
                'type': 'date',
                'placeholder': 'Ingrese la fecha del ingreso'
            }), 
            'valor': forms.NumberInput(attrs={
                'class': clase_formulario,
                'min': '0',
                'step': '1',  # Para enteros, no decimales
                'placeholder': 'Valor'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': clase_formulario,
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


#--------------------REPORTE DE INGRESOS--------------------#   



class ReporteIngresoForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)      
        # Aplicar clases CSS a campos con errores después de la validación
            # Aplicar clases CSS a campos con errores después de la validación
        if hasattr(self, 'errors') and self.errors:
            for field_name, field in self.fields.items():
                if field_name in self.errors:
                    # Preservar las clases existentes
                    current_classes = field.widget.attrs.get('class', '')
                    if 'is-invalid' not in current_classes:
                        field.widget.attrs['class'] = f"{current_classes} is-invalid"

                        
    inicio = forms.DateField(
        required=True,
        error_messages={
            'required': 'La fecha inicial es obligatoria.',
            'invalid': 'Ingrese una fecha válida.'
        },
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'id': 'id_fecha_inicio',
                'class': clase_formulario,
                'placeholder': 'dd/mm/aaaa',
                'novalidate': True, 
            }
        )
    )

    fin = forms.DateField(
        required=True,
        error_messages={
            'required': 'La fecha final es obligatoria.',
            'invalid': 'Ingrese una fecha válida.'
        },
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'id': 'id_fecha_fin',
                'class': clase_formulario,
                'placeholder': 'dd/mm/aaaa',
                'novalidate': True,  # Desactiva la validación HTML5
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get('inicio')
        fin = cleaned_data.get('fin')

        if inicio and fin and inicio > fin:
            raise forms.ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin.")
        
        return cleaned_data
