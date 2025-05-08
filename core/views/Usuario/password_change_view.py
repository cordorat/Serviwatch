from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from core.forms.password_change_form import PasswordChangeForm
from core.services.password_change_service import validate_current_password, validate_new_password, change_password

@login_required
@require_http_methods(["GET", "POST"])
def password_change_view(request):
    url_cambiar_contrasenia= 'usuario/password_change.html'
    if request.method == 'GET':
        return render(request, url_cambiar_contrasenia, {'form': PasswordChangeForm()})

    form = PasswordChangeForm(request.POST)
    
    if not form.is_valid():
        return render(request, url_cambiar_contrasenia, {'form': form})

    contrasenia_actual = form.cleaned_data.get('contrasenia_actual')
    contrasenia_nueva = form.cleaned_data.get('contrasenia_nueva')
    
    is_valid_current, error = validate_current_password(request.user, contrasenia_actual)
    if not is_valid_current:
        form.add_error('contrasenia_actual', error)
        return render(request, url_cambiar_contrasenia, {'form': form})
    
    is_valid_new, error = validate_new_password(contrasenia_actual, contrasenia_nueva)
    if not is_valid_new:
        form.add_error('contrasenia_nueva', error)
        return render(request, url_cambiar_contrasenia, {'form': form})
    
    success, message = change_password(request.user, contrasenia_nueva)
    if not success:
        return render(request, url_cambiar_contrasenia, {
            'form': form,
            'error': message
        })
    
    update_session_auth_hash(request, request.user)

    return render(request, url_cambiar_contrasenia, {
        'form': PasswordChangeForm(),  # Limpia el formulario
        'success': message  # Muestra el modal
    })
