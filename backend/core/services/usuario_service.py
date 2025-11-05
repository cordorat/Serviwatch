from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

def get_all_usuarios():
    return User.objects.all()

def crear_usuario(username, password, email):
    
    if User.objects.filter(username=username).exists():
        raise ValidationError("El nombre de usuario ya existe.")
    if User.objects.filter(email=email).exists():
        raise ValidationError("El correo electrónico ya está en uso.")
    
    if len(username) < 8:
        raise ValidationError("El nombre de usuario debe tener al menos 8 caracteres.")
    
    try:
        validate_password(password, user=User(username=username))
    except ValidationError as e:
        raise ValidationError({'password':e.messages})
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    return user