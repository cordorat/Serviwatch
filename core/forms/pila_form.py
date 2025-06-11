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
            Pilas.objects.filter(codigo=codigo).exclude(pk=self.instance.pk).exists()
        else:
            if Pilas.objects.filter(codigo=codigo).exists():
                raise forms.ValidationError("Este codigo ya esta registrado")
        return codigo
    
        
    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')

        if not cantidad.isdigit():
            raise forms.ValidationError("La cantidad solo debe contener números.")
        
        cantidad = cantidad.lstrip('0')

        return cantidad
