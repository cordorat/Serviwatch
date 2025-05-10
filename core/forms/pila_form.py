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
    precio = forms.CharField(
        required=True,
        max_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': 'precio'
        }),
        error_messages={
            'required': 'El precio es obligatorio',
            'max_length': 'El precio debe tener maximo 6 caracteres'
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
        fields = ['codigo', 'precio', 'cantidad']

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if self.instance and self.instance.pk:
            Pilas.objects.filter(codigo=codigo).exclude(pk=self.instance.pk).exists()
        else:
            if Pilas.objects.filter(codigo=codigo).exists():
                raise forms.ValidationError("Este codigo ya esta registrado")
        return codigo
    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if not precio.isdigit():
            raise forms.ValidationError("El precio solo debe contener números.")
        return precio
        
    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if not cantidad.isdigit():
            raise forms.ValidationError("La cantidad solo debe contener números.")
        return cantidad
