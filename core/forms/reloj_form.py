from django import forms
from core.models.reloj import Reloj

class RelojForm(forms.ModelForm):
    marca = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'Marca'}),
        error_messages={
            'required': 'La marca es obligatoria',
            'max_length': 'La marca debe tener máximo 30 caracteres'
        }
    )
    referencia = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'Referencia'}),
        error_messages={
            'required': 'La referencia es obligatoria',
            'max_length': 'La referencia debe tener máximo 30 caracteres'
        }
    )
    precio = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': 'Precio','class': 'form-control'}),
        error_messages={'required': 'El precio es obligatorio',
                        'max_length': 'El precio no puede exceder los 20 caracteres'}
    )
    dueño = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Dueño'}),
        error_messages={
            'required': 'El dueño es obligatorio',
            'max_length': 'El dueño debe tener máximo 50 caracteres'
        }
    )
    descripcion = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.Textarea(attrs={'placeholder': 'Descripción'}),
        error_messages={
            'required': 'La descripción es obligatoria',
            'max_length': 'La descripción debe tener máximo 150 caracteres'
        }
    )
    tipo = forms.ChoiceField(
        required=True,
        choices=[('NUEVO', 'Nuevo'), ('USADO', 'Usado'), ('SEMI', 'Seminuevo')],
        widget=forms.Select(attrs={'placeholder': 'Tipo'}),
        error_messages={'required': 'El tipo es obligatorio'}
    )
    estado = forms.ChoiceField(
        required=True,
        choices=[('VENDIDO', 'Vendido'), ('DISPONIBLE', 'Disponible')],
        widget=forms.Select(attrs={'placeholder': 'Estado'}),
        error_messages={'required': 'El estado es obligatorio'}
    )
    fecha_venta = forms.DateField(
        input_formats=['%d/%m/%Y'],
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Fecha de venta', 'type': 'text'}),
        error_messages={'invalid': 'Formato de fecha inválido. Use DD/MM/AA.'}
    )
    pagado = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput()
    )

    class Meta:
        model = Reloj
        fields = ['marca', 'referencia', 'precio', 'dueño', 'descripcion', 'tipo', 'estado', 'fecha_venta', 'pagado']
        # No incluir 'comision' aquí porque es un campo no editable

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estado'].initial = 'DISPONIBLE'  # Asegúrate de que el estado tenga un valor por defecto
        self.fields['pagado'].initial = False

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')

        if not precio.isdigit():
            raise forms.ValidationError("El precio solo puede ser numerico")
        
        precio = int(precio)

        if precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor que cero.')

        if precio > 999999999999:
            raise forms.ValidationError('El precio es demasiado grande.')

        return precio
    
    def clean_comision(self):
        comision = self.cleaned_data.get('comision')
        precio = self.cleaned_data.get('precio')

        if not comision.isdigit():
            raise forms.ValidationError("La comision solo puede ser numerico")
        
        comision = int(comision)
        comision = precio * 0.2

        if comision <= 0:
            raise forms.ValidationError('La comision debe ser mayor que cero.')

        if comision > 999999999999:
            raise forms.ValidationError('La comision es demasiado grande.')

        return comision

    def clean(self):
        cleaned_data = super().clean()
        estado = cleaned_data.get('estado')
        fecha_venta = cleaned_data.get('fecha_venta')

        if estado == 'VENDIDO' and not fecha_venta:
            self.add_error('fecha_venta', 'La fecha de venta es obligatoria cuando el estado es "Vendido".')

        return cleaned_data
