from django import forms
from core.models import Reparacion, Cliente, Empleado
from django.core.exceptions import ValidationError
import datetime


class ClienteChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.nombre} - {obj.apellido} - {obj.telefono}"

class ReparacionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].required = False  
        self.fields['cliente'].widget.attrs['class'] = 'form-control'
        self.fields['cliente'].widget.attrs['placeholder'] = 'Seleccione un cliente'
        for field in self.fields:
            if self[field].errors:
                self.fields[field].widget.attrs.update({'class': 'form-control is-invalid'})
            
    cliente = ClienteChoiceField(
        queryset=Cliente.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control select',
        }),
        empty_label="Seleccione un cliente"
    )
    
    tecnico = forms.ModelChoiceField(
        queryset=Empleado.objects.all(),
        empty_label="Seleccione un técnico",
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control form-span text-secondary'
        })
    )
    
    fecha_entrega_estimada = forms.DateField(
        input_formats=['%d/%m/%Y'],
        required=False,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'id': 'id_fecha_entrega_estimada',
                'placeholder': 'Fecha estimada entrega',
                'autocomplete': 'off'
            }
        )
    )
    

    class Meta:
        model = Reparacion
        fields = ['cliente', 'marca_reloj', 'descripcion', 'codigo_orden',
                 'fecha_entrega_estimada', 'precio', 'espacio_fisico', 
                 'estado', 'tecnico']
        error_messages = {
            'cliente': {
                'required': 'Por favor seleccione un cliente',
            },
            'marca_reloj': {
                'required': 'La marca del reloj es obligatoria',
                'max_length': 'La marca no puede tener más de 100 caracteres'
            },
            'descripcion': {
                'required': 'La descripción es obligatoria',
                'min_length': 'La descripción debe tener al menos 10 caracteres',
                'max_length': 'La descripción no puede tener más de 500 caracteres'
            },
            'codigo_orden': {
                'required': 'El código de orden es obligatorio',
                'invalid': 'El código debe ser numérico',
                'unique': 'Este código de orden ya existe'
            },
            'fecha_entrega_estimada': {
                'required': 'La fecha de entrega es obligatoria',
                'invalid': 'Por favor ingrese una fecha válida'
            },
            'precio': {
                'required': 'El precio es obligatorio',
                'invalid': 'Por favor ingrese un número válido',
                'min_value': 'El precio debe ser mayor a 0',
                'max_value': 'El precio no puede ser mayor a 1,000,000'
            },
            'espacio_fisico': {
                'required': 'El espacio físico es obligatorio',
                'max_length': 'El espacio físico no puede tener más de 50 caracteres'
            },
            'estado': {
                'required': 'Por favor seleccione un estado',
                'invalid_choice': 'Estado no válido'
            },
            'tecnico': {
                'required': 'Por favor seleccione un técnico',
                'invalid_choice': 'Técnico no válido'
            }
        }
        widgets = {
            'marca_reloj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Marca del reloj'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
            'codigo_orden': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código de orden'}),
            'fecha_entrega_estimada': forms.DateInput(attrs={
                'class': 'form-control text-secondary',
                'type': 'date',
                'placeholder': 'Fecha de entrega estimada'
            }),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio'}),
            'espacio_fisico': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Espacio físico'}),
            'estado': forms.Select(attrs={'class': 'form-span form-control text-secondary', 'placeholder': 'Estado'}),
            'tecnico': forms.Select(attrs={'class': 'form-control form-span text-secondary'}),
        }
    def clean_cliente(self):
        cliente = self.cleaned_data.get('cliente')
        if not cliente:
            raise forms.ValidationError("Debe seleccionar un cliente.")
        return cliente
        

    def clean_marca_reloj(self):
        marca = self.cleaned_data.get('marca_reloj')
        if not marca:
            raise forms.ValidationError("La marca del reloj es obligatoria.")
        if len(marca) > 100:
            raise forms.ValidationError("La marca del reloj no puede tener más de 100 caracteres.")
        return marca

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if not descripcion:
            raise forms.ValidationError("La descripción es obligatoria.")
        if len(descripcion) < 10:
            raise forms.ValidationError("La descripción debe tener al menos 10 caracteres.")
        if len(descripcion) > 500:
            raise forms.ValidationError("La descripción no puede tener más de 500 caracteres.")
        return descripcion

    def clean_codigo_orden(self):
        codigo = self.cleaned_data.get('codigo_orden')
        
        # Validaciones existentes
        if not codigo:
            raise forms.ValidationError("El código de orden es obligatorio.")
        if not str(codigo).isdigit():
            raise forms.ValidationError("El código de orden debe ser numérico.")
        if len(str(codigo)) > 10:
            raise forms.ValidationError("El código de orden no puede tener más de 10 dígitos.")
        
        # Verificar si el código ya existe, excluyendo la instancia actual
        existing_query = Reparacion.objects.filter(codigo_orden=codigo)
        
        # Si estamos editando una reparación existente, excluirla de la validación
        if self.instance and self.instance.pk:
            existing_query = existing_query.exclude(pk=self.instance.pk)
        
        if existing_query.exists():
            raise forms.ValidationError("Este código de orden ya existe.")
        
        return codigo

    def clean_fecha_entrega_estimada(self):
        fecha = self.cleaned_data.get('fecha_entrega_estimada')
        if not fecha:
            raise forms.ValidationError("La fecha de entrega estimada es obligatoria.")
        if fecha < datetime.date.today():
            raise forms.ValidationError("La fecha de entrega no puede ser anterior a hoy.")
        return fecha

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if not precio:
            raise forms.ValidationError("El precio es obligatorio.")
        if precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a 0.")
        if precio > 1000000:
            raise forms.ValidationError("El precio no puede ser mayor a 1,000,000.")
        return precio

    def clean_espacio_fisico(self):
        espacio = self.cleaned_data.get('espacio_fisico')
        if not espacio:
            raise forms.ValidationError("El espacio físico es obligatorio.")
        if len(espacio) > 50:
            raise forms.ValidationError("El espacio físico no puede tener más de 50 caracteres.")
        return espacio
    def clean_cliente(self):
        cliente = self.cleaned_data.get('cliente')
        if not cliente:
            raise forms.ValidationError("Por favor seleccione un cliente.")
        return cliente
    
    def clean_tecnico(self):
        tecnico = self.cleaned_data.get('tecnico')
        if not tecnico:
            raise forms.ValidationError("Debe seleccionar un técnico para la reparación.")
        return tecnico

    def clean(self):
        cleaned_data = super().clean()
        cliente = cleaned_data.get('cliente')
        tecnico = cleaned_data.get('tecnico')
        estado = cleaned_data.get('estado')

        if not cliente:
            raise forms.ValidationError("Debe seleccionar un cliente.")
        
        if not tecnico:
            raise forms.ValidationError("Debe seleccionar un técnico.")

        if not estado:
            raise forms.ValidationError("Debe seleccionar un estado.")

        return cleaned_data
