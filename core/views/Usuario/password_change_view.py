from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from core.forms.password_change_form import PasswordChangeForm

@login_required
@require_http_methods(["GET", "POST"])
def password_change_view(request):
    url_cambiar_contrasenia = 'usuario/password_change.html'
    if request.method == 'GET':
        return render(request, url_cambiar_contrasenia, {'form': PasswordChangeForm()})

    # Pasar el usuario y los datos POST al formulario
    form = PasswordChangeForm(request.POST, user=request.user)
    
    if not form.is_valid():
        return render(request, url_cambiar_contrasenia, {'form': form})

    contrasenia_actual = form.cleaned_data.get('contrasenia_actual')
    contrasenia_nueva = form.cleaned_data.get('contrasenia_nueva')
    
    # Validar contraseña actual
    if not request.user.check_password(contrasenia_actual):
        form.add_error('contrasenia_actual', 'Contraseña incorrecta')
        return render(request, url_cambiar_contrasenia, {'form': form})
    
    # Validar que la nueva contraseña sea diferente
    if contrasenia_actual == contrasenia_nueva:
        form.add_error('contrasenia_nueva', 'La contraseña nueva no puede ser igual a la anterior')
        return render(request, url_cambiar_contrasenia, {'form': form})
    
    # Cambiar la contraseña
    try:
        request.user.set_password(contrasenia_nueva)
        request.user.save()
        
        # Actualizar la sesión para evitar cerrarla al cambiar la contraseña
        update_session_auth_hash(request, request.user)
        
        # Devolver el formulario limpio con mensaje de éxito
        return render(request, url_cambiar_contrasenia, {
            'form': PasswordChangeForm(),
            'success': 'Su contraseña ha sido actualizada correctamente'
        })
    except Exception as e:
        form.add_error(None, f'Error al cambiar la contraseña: {str(e)}')
        return render(request, url_cambiar_contrasenia, {'form': form})