from django import forms
from core.models.empleado import Empleado
from datetime import date


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
            'class': 'validate form-control',
            'placeholder': 'Cédula'
        })
    )
    celular = forms.CharField(
        label="Celular",
        required=True,
        max_length=10,
        min_length=10,
        error_messages={
            'max_length': "El celular debe tener exactamente 10 dígitos.",
            'min_length': "El celular debe tener exactamente 10 dígitos."
        },
        widget=forms.TextInput(attrs={
            'class': 'validate form-control',
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
            'class': 'validate form-control',
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
                'class': 'form-control text-secondary',
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
                'class': 'form-control text-secondary',
                'placeholder': 'Fecha de ingreso',
            }
        )
    )

    cargo = forms.ChoiceField(
        choices=[('', 'Seleccione un cargo')] + list(Empleado.CARGO_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control form-span text-secondary',
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
                'class': 'validate form-control',
                'placeholder': 'Nombre(s)'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'validate form-control',
                'placeholder': 'Apellido(s)'
            }),
            'celular': forms.TextInput(attrs={
                'class': 'validate form-control',
                'placeholder': 'Teléfono'
            }),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date', 'class': 'form-control text-secondary', 'placeholder': 'Fecha de ingreso'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control text-secondary'}),
            'cargo': forms.Select(attrs={'class': 'form-control form-span text-secondary'}),
            'estado': forms.Select(attrs={'class': 'form-control form-span text-secondary'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre and len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return nombre

    def clean_cedula(self):
        
        cedula = self.cleaned_data.get('cedula')

        # Validaciones básicas de formato
        if not cedula.isdigit():
            raise forms.ValidationError("La cédula debe contener solo números.")

        if len(cedula) > 15:
            raise forms.ValidationError(
                "La cédula no puede tener más de 15 dígitos.")

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
                "El celular debe tener exactamente 10 dígitos.")
        return celular

    def clean_salario(self):
        salario = self.cleaned_data.get('salario')
        if not salario.isdigit():
            raise forms.ValidationError("El salario debe ser numérico.")
        if len(salario) > 8:
            raise forms.ValidationError(
                "El salario no puede tener más de 8 dígitos.")
        return salario
    
    def clean_apellidos(self):
        apellidos = self.cleaned_data.get('apellidos')
        if apellidos and len(apellidos) < 2:
            raise forms.ValidationError("Los apellidos deben tener al menos 2 caracteres.")
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
