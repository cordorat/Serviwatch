from django import forms
from core.models import Cliente
from django.db.models import Q
import re

clase_form_validate = 'validate form-control'

class ClienteForm(forms.ModelForm):
    telefono = forms.CharField(
        label="Teléfono",
        required=True,
        max_length=10,
        min_length=10,
        widget=forms.TextInput(attrs={
            'class': clase_form_validate,
            'placeholder': 'Telefono',
        }),
        error_messages={
            'required': 'El número de teléfono es obligatorio.',
            'min_length': 'El número de teléfono debe tener exactamente 10 dígitos.',
            'invalid': 'El número de teléfono solo puede contener números.'
        }
    )

    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': clase_form_validate,
                'placeholder': 'Nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': clase_form_validate,
                'placeholder': 'Apellido'
            }),
        }
        error_messages = {
            'nombre': {
                'required': 'El nombre es obligatorio.',
                'max_length': 'El nombre no puede tener más de 20 caracteres.',
                'invalid': 'El nombre solo puede contener letras.'
            },
            'apellido': {
                'required': 'El apellido es obligatorio.',
                'max_length': 'El apellido no puede tener más de 30 caracteres.',
                'invalid': 'El apellido solo puede contener letras.'
            }
        }

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')

        if not telefono.isdigit():
            raise forms.ValidationError("El número de teléfono solo debe contener números.")

        if len(telefono) != 10:
            raise forms.ValidationError("El número de teléfono debe tener exactamente 10 dígitos.")

        return telefono
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        # Permitir espacios para nombres compuestos
        if nombre and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise forms.ValidationError('El nombre solo debe contener letras y espacios.')
        
        # Verificar que cada parte del nombre tenga al menos 2 caracteres
        palabras = nombre.split()
        for palabra in palabras:
            if len(palabra) < 2:
                raise forms.ValidationError('Cada nombre debe tener al menos 2 letras.')
        
        return nombre
    
    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')
        # Permitir espacios para nombres compuestos
        if apellido and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', apellido):
            raise forms.ValidationError('El nombre solo debe contener letras y espacios.')
        
        # Verificar que cada parte del nombre tenga al menos 2 caracteres
        palabras = apellido.split()
        for palabra in palabras:
            if len(palabra) < 2:
                raise forms.ValidationError('Cada nombre debe tener al menos 2 letras.')
        
        return apellido
    
    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        apellido = cleaned_data.get('apellido')
        telefono = cleaned_data.get('telefono')
        
        if nombre and apellido and telefono:
            # Consulta para buscar clientes con los mismos datos (insensible a mayúsculas/minúsculas)
            query = Q(nombre__iexact=nombre) & Q(apellido__iexact=apellido) & Q(telefono=telefono)
            
            # Verificar si existe un cliente con los mismos datos
            if Cliente.objects.filter(query).exists():
                # Add the error to a specific field instead of the entire form
                self.add_error(
                    'nombre', "Este cliente ya esta registrado."
                    )
        return cleaned_data
