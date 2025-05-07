from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

def validate_current_password(user, contraseña_actual):
    """Valida que la contraseña actual sea correcta"""
    if not check_password(contraseña_actual, user.password):
        return False, "Contraseña incorrecta"
    return True, None

def validate_new_password(contraseña_actual, contraseña_nueva):
    """Valida que la contraseña nueva no sea igual a la actual"""
    if contraseña_actual == contraseña_nueva:
        return False, "Contraseña nueva no puede ser igual a la anterior"
    return True, None

def change_password(user, contraseña_nueva):
    """Cambia la contraseña del usuario"""
    try:
        user.set_password(contraseña_nueva)
        user.save()
        return True, "Su contraseña ha sido actualizada correctamente"
    except Exception as e:
        return False, f"Error al actualizar la contraseña: {str(e)}"