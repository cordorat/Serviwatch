from django import forms
from core.models.reloj import Reloj

class RelojForm(forms.ModelForm):
    marca = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'Marca'
        }),
        error_messages={
            'required': 'La marca es obligatoria',
            'max_length': 'La marca debe tener maximo 30 caracteres'
        }
    )
    referencia = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'Referencia'
        }),
        error_messages={
            'required': 'La referencia es obligatoria',
            'max_length': 'La referencia debe tener maximo 30 caracteres'
        }
    )
    precio = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Precio'
        }),
        error_messages={
            'required': 'El precio es obligatorio',
            'max_length': 'El precio debe tener maximo 20 caracteres'
        }
    )
    dueño = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Dueño'
        }),
        error_messages={
            'required': 'El dueño es obligatorio',
            'max_length': 'El dueño debe tener maximo 50 caracteres'
        }
    )
    descripcion = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.Textarea(attrs={
            'placeholder': 'Descripción'
        }),
        error_messages={
            'required': 'La descripción es obligatoria',
            'max_length': 'La descripción debe tener maximo 150 caracteres'
        }
    )
    tipo = forms.ChoiceField(
        required=True,
        choices=[
            ('NUEVO', 'Nuevo'),
            ('USADO', 'Usado'),
            ('SEMI', 'Seminuevo')
        ],
        widget=forms.Select(attrs={
            'placeholder': 'Tipo'
        }),
        error_messages={
            'required': 'El tipo es obligatorio'
        }
    )
    estado = forms.ChoiceField(
        required=True,
        choices=[
            ('VENDIDO', 'Vendido'),
            ('DISPONIBLE', 'Disponible')
        ],
        widget=forms.Select(attrs={
            'placeholder': 'Estado'
        }),
        error_messages={
            'required': 'El estado es obligatorio'
        }
    )
    fecha_venta = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Fecha de venta',
            'type': 'date'
        }),
        input_formats=['%d/%m/%y'],
        error_messages={
            'invalid': 'Formato de fecha inválido. Use DD/MM/AA.'
        }
    )
    comision = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Comisión',
            'readonly': 'readonly'
        })
    )
    pagado = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'placeholder': 'Pagado'
        },
        initial=False,
        )
    )

    class Meta:
        model = Reloj
        fields = ['marca', 'referencia', 'precio', 'dueño', 'descripcion', 'tipo', 'estado', 'fecha_venta', 'comision', 'pagado']

    def clean_fecha_venta(self):
        estado = self.cleaned_data.get('estado')
        fecha_venta = self.cleaned_data.get('fecha_venta')

        if estado == 'VENDIDO' and not fecha_venta:
            raise forms.ValidationError('La fecha de venta es obligatoria cuando el estado es "Vendido".')
        
        return fecha_venta

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')

        if not precio:
            raise forms.ValidationError('El precio es obligatorio')

        if len(str(precio)) > 20:
            raise forms.ValidationError("Precio demasiado grande")

        try:
            precio = float(precio)
        except ValueError:
            raise forms.ValidationError('El precio debe ser un número válido.')

        if precio <= 0:
            raise forms.ValidationError('El precio debe ser un valor positivo.')

        return precio

    

    def clean(self):
        cleaned_data = super().clean()
        
        estado = cleaned_data.get('estado')
        fecha_venta = cleaned_data.get('fecha_venta')
        pagado = cleaned_data.get('pagado')
        precio = cleaned_data.get('precio')

        if estado == 'VENDIDO' and not fecha_venta:
            self.add_error('fecha_venta', 'La fecha de venta es obligatoria cuando el estado es "Vendido".')

        # Calcular comisión si precio es válido
        if precio:
            try:
                precio_float = float(precio)
                cleaned_data['comision'] = round(precio_float * 0.2, 2)
            except ValueError:
                self.add_error('precio', 'El precio debe ser un número válido.')

        return cleaned_data


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comision'].widget.attrs['readonly'] = True  # Hacer el campo de comision solo lectura
        self.fields['estado'].initial = 'DISPONIBLE'  # Establecer el estado por defecto a 'DISPONIBLE'
        self.fields['pagado'].initial = False  # Establecer el pagado por defecto a False