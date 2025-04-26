from django import forms
from core.models.empleado import Empleado

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = [
            'cedula', 'nombre', 'apellidos', 
            'fecha_ingreso', 'fecha_nacimiento', 
            'celular', 'cargo', 'salario', 'estado'
        ]

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if not str(cedula).isdigit():
            raise forms.ValidationError("La cédula debe contener solo números.")
        if len(str(cedula)) > 15:
            raise forms.ValidationError("La cédula no puede tener más de 15 dígitos.")
        if Empleado.objects.filter(cedula=cedula).exists():
            raise forms.ValidationError("Empleado ya existente.")
        return cedula

    def clean_celular(self):
        celular = self.cleaned_data.get('celular')
        if not str(celular).isdigit():
            raise forms.ValidationError("El celular debe contener solo números.")
        if len(str(celular)) != 10:
            raise forms.ValidationError("El celular debe tener exactamente 10 dígitos.")
        return celular

    def clean_salario(self):
        salario = self.cleaned_data.get('salario')
        if not str(salario).isdigit():
            raise forms.ValidationError("El salario debe ser numérico.")
        if len(str(salario)) > 8:
            raise forms.ValidationError("El salario no puede tener más de 8 dígitos.")
        return salario
