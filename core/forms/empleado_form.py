from django import forms
from core.models.empleado import Empleado
from datetime import date
import re

clase_formulario_validate = "validate form-control"
clase_formulario_control = 'form-control text-secondary'
clase_formulario_control_span = 'form-control form-span text-secondary'
mensaje_tamaño_celular = "El celular debe tener exactamente 10 dígitos."

class EmpleadoForm(forms.ModelForm):
    cedula = forms.CharField(
        label="Cédula",
        required=True,
        max_length=15,
        error_messages={
            'unique': "La cédula ya existe.",
            'max_length': "La cédula no puede tener más de 15 dígitos."
        },
        widget=forms.TextInput(attrs={
            'class': clase_formulario_validate,
            'placeholder': 'Cédula'
        })
    )
    celular = forms.CharField(
        label="Celular",
        required=True,
        max_length=10,
        min_length=10,
        error_messages={
            'max_length': mensaje_tamaño_celular,
            'min_length': mensaje_tamaño_celular
        },
        widget=forms.TextInput(attrs={
            'class': clase_formulario_validate,
            'placeholder': 'Teléfono'
        })
    )
    salario = forms.CharField(
        label="Salario",
        required=False,
        max_length=8,
        error_messages={
            'max_length': "El salario no puede tener más de 8 dígitos."
        },
        widget=forms.TextInput(attrs={
            'class': clase_formulario_validate,
            'placeholder': 'Salario'
        })
    )

    fecha_nacimiento = forms.DateField(
        input_formats=['%d/%m/%Y'],
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'text',
                'id': 'id_fecha_nacimiento',
                'class': clase_formulario_control,
                'placeholder': 'Fecha de nacimiento',
            }
        )
    )

    fecha_ingreso = forms.DateField(
        input_formats=['%d/%m/%Y'],
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'text',
                'id': 'id_fecha_ingreso',
                'class': clase_formulario_control,
                'placeholder': 'Fecha de ingreso',
            }
        )
    )

    cargo = forms.ChoiceField(
        choices=[('', 'Seleccione un cargo')] + list(Empleado.CARGO_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': clase_formulario_control_span,
            'placeholder': 'Cargo'
        })
    )

    class Meta:
        model = Empleado
        fields = [
            'cedula', 'nombre', 'apellidos',
            'fecha_ingreso', 'fecha_nacimiento',
            'celular', 'cargo', 'salario', 'estado'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': clase_formulario_validate,
                'placeholder': 'Nombre(s)'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': clase_formulario_validate,
                'placeholder': 'Apellido(s)'
            }),
            'celular': forms.TextInput(attrs={
                'class': clase_formulario_validate,
                'placeholder': 'Teléfono'
            }),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date', 'class': clase_formulario_control, 'placeholder': 'Fecha de ingreso'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': clase_formulario_control}),
            'cargo': forms.Select(attrs={'class': clase_formulario_control_span}),
            'estado': forms.Select(attrs={'class': clase_formulario_control_span}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        # Permitir espacios para nombres compuestos
        if nombre and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise forms.ValidationError('El nombre solo debe contener letras y espacios.')
        
        # Verificar que cada parte del nombre tenga al menos 2 caracteres
        palabras = nombre.split()
        for palabra in palabras:
            if len(palabra) < 2:
                raise forms.ValidationError('Cada nombre debe tener al menos 2 letras.')
        
        return nombre

    def clean_cedula(self):
        
        cedula = self.cleaned_data.get('cedula')

        # Validaciones básicas de formato
        if not cedula.isdigit():
            raise forms.ValidationError("La cédula debe contener solo números.")

        if len(cedula) > 10:
            raise forms.ValidationError(
                "La cédula no puede tener más de 10 dígitos.")

        # Comprobar unicidad solo para nuevos empleados, no para ediciones
        if not self.instance.pk:  # Si es un nuevo empleado (no tiene ID)
            if Empleado.objects.filter(cedula=cedula).exists():
                raise forms.ValidationError("Empleado ya existente.")
        else:  # Si es una edición
            # Verificar si hay otro empleado (diferente al actual) con esta cédula
            existing = Empleado.objects.filter(
                cedula=cedula).exclude(pk=self.instance.pk).exists()
            if existing:
                raise forms.ValidationError(
                    "Existe otro empleado con esta cédula.")

        return cedula

    def clean_celular(self):
        celular = self.cleaned_data.get('celular')
        if not celular.isdigit():
            raise forms.ValidationError(
                "El celular debe contener solo números.")
        if len(celular) != 10:
            raise forms.ValidationError(
                mensaje_tamaño_celular)
        return celular

    def clean_salario(self):
        salario = self.cleaned_data.get('salario')
        if not salario.isdigit():
            raise forms.ValidationError("El salario debe ser numérico.")
        
        salario = salario.lstrip('0')  # Eliminar ceros a la izquierda

        if len(salario) > 8:
            raise forms.ValidationError(
                "El salario no puede tener más de 8 dígitos.")
        return salario
    
    def clean_apellidos(self):
        apellidos = self.cleaned_data.get('apellidos')
        # Permitir espacios para nombres compuestos
        if apellidos and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', apellidos):
            raise forms.ValidationError('El nombre solo debe contener letras y espacios.')
        
        # Verificar que cada parte del nombre tenga al menos 2 caracteres
        palabras = apellidos.split()
        for palabra in palabras:
            if len(palabra) < 2:
                raise forms.ValidationError('Cada nombre debe tener al menos 2 letras.')
        
        return apellidos
    
    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento:
            # Calcular la edad
            hoy = date.today()
            edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            
            # Verificar si es menor de edad (menos de 18 años)
            if edad < 18:
                raise forms.ValidationError("El empleado debe ser mayor de edad (18 años o más).")
        
        return fecha_nacimiento
    
    def clean_fecha_ingreso(self):
        fecha_ingreso = self.cleaned_data.get('fecha_ingreso')
        if fecha_ingreso:
            # Verificar que la fecha de ingreso no sea futura
            hoy = date.today()
            if fecha_ingreso > hoy:
                raise forms.ValidationError("La fecha de ingreso no puede ser una fecha futura.")
        
        return fecha_ingreso
