from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from core.forms.password_change_form import PasswordChangeForm

@login_required
@require_http_methods(["GET", "POST"])
def password_change_view(request):
    """
    Vista para cambiar la contraseña del usuario.
    Utiliza el formulario PasswordChangeForm para validar y procesar el cambio.
    """
    if request.method == 'GET':
        # Pasar el usuario al formulario
        form = PasswordChangeForm(user=request.user)
        return render(request, 'usuario/password_change.html', {'form': form})

    # Pasar el usuario y los datos POST al formulario
    form = PasswordChangeForm(request.POST, user=request.user)
    
    if not form.is_valid():
        return render(request, 'usuario/password_change.html', {'form': form})
    
    # El formulario ya realizó todas las validaciones necesarias
    # Usar el método save del formulario para cambiar la contraseña
    form.save()
    
    # Actualizar la sesión para evitar cerrarla al cambiar la contraseña
    update_session_auth_hash(request, request.user)

    # Mensaje de éxito para el usuario
    messages.success(request, "Tu contraseña ha sido cambiada correctamente.")
    
    # Redirigir o mostrar el éxito con un formulario limpio
    return render(request, 'usuario/password_change.html', {
        'form': PasswordChangeForm(user=request.user),  # Formulario limpio
        'success': "Contraseña actualizada correctamente"  # Para el modal
    })
