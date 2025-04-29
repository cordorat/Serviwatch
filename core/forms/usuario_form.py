from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import password_validation

class FormularioRegistroUsuario(UserCreationForm):
    """
    Formulario para registro de usuario que extiende UserCreationForm
    pero personaliza los mensajes de error y ayuda.
    """
    email = forms.EmailField(
        required=True,
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        })
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super(FormularioRegistroUsuario, self).__init__(*args, **kwargs)
        
        # Personalizar mensajes de ayuda
        self.fields['username'].help_text = "Obligatorio. 50 caracteres o menos."
        self.fields['email'].help_text = "Debe contener un @ y terminar en .com, .org, .net, etc."
        self.fields['password1'].help_text = "La contraseña debe tener al menos 8 caracteres y máximo 16 caracteres. Debe tener números, letras y caracteres especiales."
        self.fields['password2'].help_text = "Repite la contraseña para verificación."
        
        # Configurar placeholders y clases para password1 y password2
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
        
        # Personalizar mensajes de error
        self.fields['username'].error_messages.update({
            'required': 'El nombre de usuario es obligatorio.',
            'unique': 'Este nombre de usuario ya está en uso.',
            'invalid': 'El nombre de usuario solo puede contener letras, números y @/./+/-/_.'
        })
        
        self.fields['email'].error_messages.update({
            'required': 'El correo electrónico es obligatorio.',
            'invalid': 'Introduzca un correo electrónico válido.'
        })
        
        self.fields['password1'].error_messages.update({
            'required': 'La contraseña es obligatoria.',
            'password_too_short': 'La contraseña debe tener al menos 8 caracteres.',
            'password_too_common': 'La contraseña es demasiado común.',
            'password_entirely_numeric': 'La contraseña no puede ser completamente numérica.'
        })
        
        self.fields['password2'].error_messages.update({
            'required': 'Debe confirmar la contraseña.'
        })
        
        # El mensaje para contraseñas que no coinciden está en error_messages
        self.error_messages.update({
            'password_mismatch': 'Las contraseñas no coinciden. Intente nuevamente.',
        })
    
    def clean_email(self):
        """Verificar que el email no esté ya en uso"""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Este correo electrónico ya está registrado.",
                code='email_exists',
            )
        return email