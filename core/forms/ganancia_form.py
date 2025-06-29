from django import forms
from core.models.egreso import Egreso
from core.models.ingreso import Ingreso
from django.utils import timezone
from datetime import timedelta
from datetime import date

clase_formulario = 'form-control text-secondary'

#--------------------REPORTE DE GANANCIAS--------------------#   


class ReporteGananciaForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)      
        # Aplicar clases CSS a campos con errores después de la validación
        if hasattr(self, 'errors') and self.errors:
            for field_name, field in self.fields.items():
                if field_name in self.errors:
                    field.widget.attrs['class'] = 'form-control is-invalid'
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


#--------------------REPORTE DE EGRESOS (LEGACY)--------------------#   


class ReporteEgresoForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)      
        # Aplicar clases CSS a campos con errores después de la validación
        if hasattr(self, 'errors') and self.errors:
            for field_name, field in self.fields.items():
                if field_name in self.errors:
                    field.widget.attrs['class'] = 'form-control is-invalid'

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