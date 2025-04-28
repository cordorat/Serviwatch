from django import forms
from core.models.empleado import Empleado

class EmpleadoForm(forms.ModelForm):
    cedula = forms.CharField(
        label="Cédula",
        required=True,
        max_length=15,
        error_messages={
            'max_length': "La cédula no puede tener más de 15 dígitos."
        },
        widget=forms.TextInput(attrs={
            'class': 'validate',
            'placeholder': 'Ingresa la cédula'
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
            'class': 'validate',
            'placeholder': 'Ingresa el número de celular'
        })
    )
    salario = forms.CharField(
        label="Salario",
        required=True,
        max_length=8,
        error_messages={
            'max_length': "El salario no puede tener más de 8 dígitos."
        },
        widget=forms.TextInput(attrs={
            'class': 'validate',
            'placeholder': 'Ingresa el salario'
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
                'class': 'validate',
                'placeholder': 'Ingresa el nombre'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'validate',
                'placeholder': 'Ingresa los apellidos'
            }),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if not cedula.isdigit():
            raise forms.ValidationError("La cédula debe contener solo números.")
        if len(cedula) > 15:
            raise forms.ValidationError("La cédula no puede tener más de 15 dígitos.")
        if Empleado.objects.filter(cedula=cedula).exists():
            raise forms.ValidationError("Empleado ya existente.")
        return cedula

    def clean_celular(self):
        celular = self.cleaned_data.get('celular')
        if not celular.isdigit():
            raise forms.ValidationError("El celular debe contener solo números.")
        if len(celular) != 10:
            raise forms.ValidationError("El celular debe tener exactamente 10 dígitos.")
        return celular

    def clean_salario(self):
        salario = self.cleaned_data.get('salario')
        if not salario.isdigit():
            raise forms.ValidationError("El salario debe ser numérico.")
        if len(salario) > 8:
            raise forms.ValidationError("El salario no puede tener más de 8 dígitos.")
        return salario
