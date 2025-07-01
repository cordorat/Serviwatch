from django import forms
from core.models.reloj import Reloj
from core.models.abono import Abono
from core.models.cliente import Cliente
from core.services.abono_service import calcular_saldo_pendiente

class ClienteChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.nombre} - {obj.apellido} - {obj.telefono}"

clase_formulario = 'form-control'
TEXT_CLASS = 'form-span form-control text-secondary'

class RelojForm(forms.ModelForm):
    marca = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': clase_formulario,
            'placeholder': 'Marca'}),
        error_messages={
            'required': 'La marca es obligatoria',
            'max_length': 'La marca debe tener máximo 30 caracteres'
        }
    )
    referencia = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': clase_formulario,
            'placeholder': 'Referencia'}),
        error_messages={
            'required': 'La referencia es obligatoria',
            'max_length': 'La referencia debe tener máximo 30 caracteres'
        }
    )
    precio = forms.CharField(
        required=True,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': clase_formulario,
            'placeholder': 'Precio',
            'type': 'text',  # Aseguramos que sea tipo text
            'inputmode': 'numeric',  # Sugiere teclado numérico en móviles
            'pattern': '[0-9]*'  # Validación HTML5 para números
        }),
        error_messages={
            'required': 'El precio es obligatorio',
            'max_length': 'El precio no puede exceder los 20 caracteres'
        }
    )

    tiene_comision = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input custom-switch',
            'id': 'tiene_comision'
        }),
    )

    comision = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': clase_formulario,
            'placeholder': 'Comisión (20%)',
            'readonly': True,
        })
    )

    dueno = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': clase_formulario,
            'placeholder': 'Dueño'}),
        error_messages={
            'required': 'El dueño es obligatorio',
            'max_length': 'El dueño debe tener máximo 50 caracteres'
        }
    )
    descripcion = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.Textarea(attrs={
            'class': clase_formulario, 'rows': 3, 'placeholder': 'Descripción'
        }),
        error_messages={
            'required': 'La descripción es obligatoria',
            'max_length': 'La descripción debe tener máximo 150 caracteres'
        }
    )
    tipo = forms.ChoiceField(
        required=True,
        choices=[('NUEVO', 'Nuevo'), ('USADO', 'Usado'), ('SEMI', 'Seminuevo')],
        widget=forms.Select(attrs={
            'class': TEXT_CLASS,
            'placeholder': 'Tipo'
        }),
        error_messages={
            'required': 'El tipo es obligatorio',
            'invalid_choice': 'Tipo no válido'
        }
    )
    estado = forms.ChoiceField(
        required=False,
        choices=[('VENDIDO', 'Vendido'), ('DISPONIBLE', 'Disponible')],
        widget=forms.Select(attrs={
            'class': TEXT_CLASS,
            'placeholder': 'Estado'
        }),
        error_messages={
            'required': 'El estado es obligatorio',
            'invalid_choice': 'Estado no válido'
        },
        initial='DISPONIBLE'
    )
    fecha_venta = forms.DateField(
        input_formats=['%d/%m/%Y'],
        required=False,
        widget=forms.DateInput(attrs={
            'class': clase_formulario,
            'type': 'text',
            'placeholder': 'Fecha de venta dd/mm/aaaa',
            'autocomplete': 'off',
            'id':'fecha_venta'
        }),
        error_messages={'invalid': 'Formato de fecha inválido. Use DD/MM/AA.'}
    )
    pagado = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    cliente = ClienteChoiceField(
        queryset=Cliente.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control select',
        }),
        empty_label="Seleccione un cliente",
    )

    metodo_pago = forms.ChoiceField(
        choices=Reloj.METODO_PAGO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': TEXT_CLASS,
            'placeholder': 'Método de pago'
        })
    )

    saldo_pendiente = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = Reloj
        fields = ['marca', 'referencia', 'precio', 'dueno', 'descripcion', 'tipo', 'estado', 'comision','fecha_venta', 'pagado', 'cliente', 'tiene_comision', 'metodo_pago', 'saldo_pendiente']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].required = False
        self.fields['cliente'].widget.attrs['class'] = 'form-control'
        self.fields['cliente'].widget.attrs['placeholder'] = 'Seleccione un cliente'
        self.fields['estado'].initial = 'DISPONIBLE'  # Asegúrate de que el estado tenga un valor por defecto
        self.fields['pagado'].initial = False
        
        # Acomodar el campo fecha_venta para que el formato sea dd/mm/yyyy en la BD
        if self.instance and self.instance.fecha_venta:
            self.initial['fecha_venta'] = self.instance.fecha_venta.strftime('%d/%m/%Y')
        
        for field in self.fields:
            if self[field].errors:
                self.fields[field].widget.attrs.update({'class': 'form-control is-invalid'})

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
        try:
            precio = self.cleaned_data.get('precio')
            tiene_comision = self.cleaned_data.get('tiene_comision')

            if not tiene_comision and precio is None:
                return 0
            
            comision = int(float(precio) * 0.2)
            return comision
        except (TypeError, ValueError):
            return 0

    def clean_fecha_venta(self):
        fecha_venta = self.cleaned_data.get('fecha_venta')
        estado = self.cleaned_data.get('estado')

        if estado == 'VENDIDO' and not fecha_venta:
            raise forms.ValidationError('La fecha de venta es obligatoria cuando el estado es Vendido')

        return fecha_venta
    
    def clean_cliente(self):
        estado = self.cleaned_data.get('estado')
        cliente = self.cleaned_data.get('cliente')

        if estado == 'VENDIDO' and not cliente:
            raise forms.ValidationError('El cliente es obligatorio cuando el estado es Vendido')
        return cliente

    def clean(self):
        cleaned_data = super().clean()
        estado = cleaned_data.get('estado')
        metodo_pago = cleaned_data.get('metodo_pago')
        precio = cleaned_data.get('precio', '0')
        tiene_comision = cleaned_data.get('tiene_comision')
        
        if estado == 'VENDIDO':
            if not metodo_pago:
                cleaned_data['metodo_pago'] = 'CONTADO'
            elif metodo_pago not in dict(Reloj.METODO_PAGO_CHOICES):
                raise forms.ValidationError({
                    'metodo_pago': 'Seleccione un método de pago válido'
                })
            
            if metodo_pago == 'CONTADO':
                cleaned_data['pagado'] = True
                cleaned_data['saldo_pendiente'] = '0'
            elif metodo_pago == 'ABONO':
                # Asegurarse de que el precio sea un string
                if self.instance and self.instance.pk:
                    abonos_existentes = Abono.objects.filter(reloj=self.instance).exists()

                    print(f"Abonos existentes: {abonos_existentes}")
                    if not abonos_existentes:
                        cleaned_data['saldo_pendiente'] = str(precio)

                    else:
                        saldo_actual = calcular_saldo_pendiente(self.instance)
                        cleaned_data['saldo_pendiente'] = saldo_actual
                        print(f"Saldo pendiente: {saldo_actual}")

        if self.instance and self.instance.pk:
            if (precio == self.instance.precio and 
                tiene_comision == self.instance.tiene_comision):
                return cleaned_data

        try:
            comision = int(precio) * 0.2 if tiene_comision else 0
            cleaned_data['comision'] = str(int(comision))

        except (ValueError, TypeError):
            cleaned_data['comision'] = '0'
                
        return cleaned_data