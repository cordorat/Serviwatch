from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password

class FormularioRegistroUsuario(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar clases CSS a campos con errores después de la validación
        if self.errors:
            for field in self.fields:
                if field in self.errors:
                     self.fields[field].widget.attrs.update({'class': 'form-control is-invalid'})
                     
    username = forms.CharField(
        label='Username:',
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'autofocus': 'off',
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        }),
        help_text='El nombre de usuario puede contener letras, números y @/./+/-/_.',
        error_messages={
            'required': 'El nombre de usuario es obligatorio.',
            'unique': 'Este nombre de usuario ya está en uso.',
            'max_length': 'El nombre de usuario no puede tener más de 50 caracteres.',
            'invalid': 'El nombre de usuario solo puede contener letras, números y @/./+/-/_.'
        }
    )
    
    email = forms.EmailField(
        required=True,
        label='Correo electrónico:',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        }),
        help_text='El correo debe tener un @ y terminar en .com, .net, .org, etc.',
        error_messages={
            'required': 'El correo electrónico es obligatorio.',
            'invalid': 'Introduzca un correo electrónico válido.'
        }
    )
    
    password1 = forms.CharField(
        required=True,
        label='Contraseña:',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        }),
        help_text='La contraseña debe tener una longitud de 8 a 16 caracteres e incluir al menos un número, una letra mayúscula, una letra minúscula y un carácter especial.',
        error_messages={
            'required': 'La contraseña es obligatoria.',
            'similar': 'La contraseña no puede ser igual al nombre de usuario.'
        }
    )
    
    password2 = forms.CharField(
        required=True,
        label='Repite la contraseña para verificación:',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        }),
        help_text='Repite exactamente la misma contraseña para verificación.',
        error_messages={
            'required': 'Debe confirmar la contraseña.',
            'similar': 'La contraseña no puede ser igual al nombre de usuario.'
        }
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def _validar_longitud_password(self, password):
        """Valida la longitud de la contraseña"""
        if not password:
            return
            
        if len(password) < 8:
            raise ValidationError(
                "La contraseña debe tener al menos 8 caracteres.",
                code='password_too_short',
            )
        elif len(password) > 16:
            raise ValidationError(
                "La contraseña no puede tener más de 16 caracteres.",
                code='password_too_long',
            )
    
    def _validar_caracteres_password(self, password):
        """Valida los requisitos de caracteres de la contraseña"""
        if not password:
            return
            
        # Lista de validaciones para hacer el código más limpio
        validaciones = [
            (not any(char.isupper() for char in password),
            "La contraseña debe incluir al menos una letra mayúscula.",
            'password_no_uppercase'),
            
            (not any(char.islower() for char in password),
            "La contraseña debe incluir al menos una letra minúscula.",
            'password_no_lowercase'),
            
            (not any(char.isdigit() for char in password),
            "La contraseña debe incluir al menos un número.",
            'password_no_numbers'),
            
            (all(char.isalnum() for char in password),
            "La contraseña debe incluir al menos un carácter especial.",
            'password_no_special')
        ]
        
        # Realizar todas las validaciones
        for condicion, mensaje, codigo in validaciones:
            if condicion:
                raise ValidationError(mensaje, code=codigo)

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        
        # Extraer las validaciones a funciones independientes
        self._validar_longitud_password(password1)
        self._validar_caracteres_password(password1)
        
        # Verificar que la contraseña no sea igual al nombre de usuario
        if password1 and self.cleaned_data.get("username") and password1.lower() == self.cleaned_data.get("username").lower():
            raise ValidationError(
                "La contraseña no puede ser igual al nombre de usuario.",
                code='password_similar',
            )
            
        return password1
    
    def clean_password2(self):

        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if (password1 and password2) and (password1 != password2):
            raise ValidationError(
                "Las contraseñas no coinciden. Por favor, inténtalo de nuevo.",
                code='password_mismatch',
            )
        
        
        return password2

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username and User.objects.filter(username=username).exists():
            raise ValidationError(
                _("El nombre de usuario ya está en uso."),
                code='username_exists',
            )
        
        if username and len(username) < 8:
            raise ValidationError(
                _("El nombre de usuario debe tener al menos 8 caracteres."),
                code='username_too_short',
            )
        
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise ValidationError(
                _("El correo electrónico ya está en uso."),
                code='email_exists',
            )
        return email
    
    def _post_clean(self):
        super()._post_clean()

        # Evita duplicar el error si ya lo tiene password1
        if 'password2' in self._errors:
            errors = []
            for error in self._errors['password2']:
                if "too similar to" in error or "similar" in error.lower():
                    errors.append("La contraseña no puede ser igual al nombre de usuario.")
                else:
                    errors.append(error)
            self._errors['password2'] = self.error_class(errors)

class FormularioEditarUsuario(forms.ModelForm):
    username = forms.CharField(
        label='Nombre de usuario',
        error_messages={
            'required': 'Este campo es obligatorio.'
        }
    )
    email = forms.EmailField(
        label='Correo electrónico',
        error_messages={
            'required': 'Este campo es obligatorio.',
            'invalid': 'Ingrese un correo electrónico válido.'
        }
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está en uso por otro usuario.")
        return email
