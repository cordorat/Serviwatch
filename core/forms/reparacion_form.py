from django import forms
from core.models import Reparacion, Cliente

class ReparacionForm(forms.ModelForm):
    descripcion = forms.CharField(
        max_length=500,
        required=True,
        error_messages={
            'max_length': "La descripción no puede superar los 500 caracteres."
        },
        widget=forms.Textarea(attrs={
            'class': 'validate',
            'placeholder': 'Descripción de la reparación'
        })
    )
    
    espacio_fisico = forms.CharField(
        max_length=15,
        required=True,
        error_messages={
            'max_length': "El espacio físico no puede tener más de 15 caracteres."
        },
        widget=forms.Textarea(attrs={
            'class': 'validate',
            'placeholder': 'Espacio físico'
        })
    )
    
    marca_reloj = forms.CharField(
        max_length=30,
        required=True,
        error_messages={
            'max_length': "La marca del reloj no puede superar los 30 caracteres."
        },
        widget=forms.Textarea(attrs={
            'class': 'validate',
            'placeholder': 'Marca del reloj'
        })
    )
    
    cliente_nombre = forms.CharField(
        max_length=50,
        required=True,
        label="Nombre del cliente",
        widget=forms.TextInput(attrs={
            'class': 'validate',
            'placeholder': 'Buscar cliente...'
        })
    )

    celular_cliente = forms.CharField(
        max_length=10,
        required=True,
        label="Celular del cliente",
        widget=forms.TextInput(attrs={
            'class': 'validate',
            'placeholder': 'Número de contacto'
        })
    )
    
    precio = forms.IntegerField(
        min_value=1,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'validate',
            'placeholder': 'Ingrese el precio'
        }),
        error_messages={
            'invalid': 'El precio debe ser un número entero.',
            'min_value': 'El precio debe ser mayor a 0.',
        }
    )

    class Meta:
        model = Reparacion
        fields = [
            'cliente', 'marca_reloj', 'descripcion', 'codigo_orden',
            'fecha_entrega_estimada', 'precio', 'espacio_fisico', 'estado', 'tecnico'
        ]
        widgets = {
            'marca_reloj': forms.TextInput(attrs={'class': 'validate', 'placeholder': 'Marca del reloj'}),
            'descripcion': forms.Textarea(attrs={'class': 'validate', 'placeholder': 'Descripción', 'rows': 4}),
            'codigo_orden': forms.TextInput(attrs={'class': 'validate', 'placeholder': 'Código de orden'}),
            'fecha_entrega_estimada': forms.DateInput(attrs={'type': 'date', 'class': 'validate'}),
            'precio': forms.NumberInput(attrs={'class': 'validate', 'placeholder': 'Precio'}),
            'espacio_fisico': forms.TextInput(attrs={'class': 'validate', 'placeholder': 'Ubicación física'}),
            'estado': forms.Select(attrs={'class': 'validate'}),
            'tecnico': forms.Select(attrs={'class': 'validate'}),
        }

    def clean_celular_cliente(self):
        celular = self.cleaned_data.get('celular_cliente')
        if not celular.isdigit():
            raise forms.ValidationError("El celular solo debe contener números.")
        if len(celular) != 10:
            raise forms.ValidationError("El celular debe tener exactamente 10 dígitos.")
        return celular

    def clean_codigo_orden(self):
        codigo = self.cleaned_data.get('codigo_orden')
        if not str(codigo).isdigit():
            raise forms.ValidationError("El código de orden debe ser numérico.")
        if len(str(codigo)) > 10:
            raise forms.ValidationError("El código de orden no puede tener más de 10 caracteres.")
        return codigo

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if not str(precio).isdigit():
            raise forms.ValidationError("El precio debe ser un número.")
        if len(str(precio)) > 10:
            raise forms.ValidationError("El precio no puede tener más de 10 dígitos.")
        return precio

    def clean_espacio_fisico(self):
        espacio = self.cleaned_data.get('espacio_fisico')
        if len(espacio) > 15:
            raise forms.ValidationError("El espacio físico no puede tener más de 15 caracteres.")
        return espacio

    def clean_marca_reloj(self):
        marca = self.cleaned_data.get('marca_reloj')
        if len(marca) > 30:
            raise forms.ValidationError("La marca del reloj no puede superar los 30 caracteres.")
        return marca

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if len(descripcion) > 500:
            raise forms.ValidationError("La descripción no puede superar los 500 caracteres.")
        return descripcion

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('cliente_nombre')
        celular = cleaned_data.get('celular_cliente')

        if nombre and celular:
            cliente = Cliente.objects.filter(nombre__icontains=nombre.strip(), telefono=celular).first()
            if not cliente:
                raise forms.ValidationError("No se encontró un cliente con ese nombre y celular.")
            # Asigna el cliente al campo del modelo
            self.instance.cliente = cliente
