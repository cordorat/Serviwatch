from django.contrib.auth import authenticate, get_user_model, login

def validate_credentials(usuario, contraseña):
    """Valida que las credenciales no estén vacías"""
    if not usuario or not contraseña:
        return False, "Ingrese las credenciales"
    return True, None

def get_user(username):
    """Obtiene un usuario por su username"""
    try:
        return get_user_model().objects.get(username=username), None
    except get_user_model().DoesNotExist:
        return None, "Usuario inexistente"

def authenticate_user(request, username, password):
    """Autentica un usuario con sus credenciales"""
    user = authenticate(request, username=username, password=password)
    if user is None:
        return None, "Usuario o contraseña incorrectos"
    return user, None

def login_user(request, user):
    """Inicia sesión y determina la redirección"""
    login(request, user)
    return 'usuario_list' if user.is_superuser else 'cliente_list'