from django import forms
from core.models.pilas import Pilas

class PilasForm(forms.ModelForm):
    codigo = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'codigo'
        }),
        error_messages={
            'required': 'El codigo es obligatorio',
            'max_length': 'El codigo debe tener maximo 30 caracteres'
        }
    )

    cantidad = forms.CharField(
        required=True,
        max_length=3,
        widget=forms.TextInput(attrs={
            'placeholder': 'cantidad'
        }),
        error_messages={
            'required': 'La cantidad es obligatorio',
            'max_length': 'La cantidad debe tener maximo 3 caracteres'
        }
    )


    class Meta:
        model = Pilas
        fields = ['codigo', 'cantidad']

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if self.instance and self.instance.pk:
            # Para edición: verificar que no exista otro con el mismo código
            if Pilas.objects.filter(codigo=codigo).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Este codigo ya esta registrado")
        else:
            # Para creación: verificar que no exista
            if Pilas.objects.filter(codigo=codigo).exists():
                raise forms.ValidationError("Este codigo ya esta registrado")
        return codigo
    
    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')

        if not cantidad.isdigit():
            raise forms.ValidationError("La cantidad solo debe contener números.")
        
        # Convertir a entero y luego a string para eliminar ceros a la izquierda
        # pero mantener el valor correcto
        cantidad_int = int(cantidad)
        if cantidad_int < 0:
            raise forms.ValidationError("La cantidad debe ser un número positivo.")
        
        return str(cantidad_int)

    # Eliminada la validación de precio, ya que no se usa en este formulario
