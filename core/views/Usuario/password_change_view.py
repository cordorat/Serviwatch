from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from core.forms.password_change_form import PasswordChangeForm
from core.services.password_change_service import validate_current_password, validate_new_password, change_password

@login_required
@require_http_methods(["GET", "POST"])
def password_change_view(request):
    if request.method == 'GET':
        return render(request, 'usuario/password_change.html', {'form': PasswordChangeForm()})

    form = PasswordChangeForm(request.POST)
    
    if not form.is_valid():
        return render(request, 'usuario/password_change.html', {'form': form})

    contraseña_actual = form.cleaned_data.get('contraseña_actual')
    contraseña_nueva = form.cleaned_data.get('contraseña_nueva')
    
    is_valid_current, error = validate_current_password(request.user, contraseña_actual)
    if not is_valid_current:
        form.add_error('contraseña_actual', error)
        return render(request, 'usuario/password_change.html', {'form': form})
    
    is_valid_new, error = validate_new_password(contraseña_actual, contraseña_nueva)
    if not is_valid_new:
        form.add_error('contraseña_nueva', error)
        return render(request, 'usuario/password_change.html', {'form': form})
    
    success, message = change_password(request.user, contraseña_nueva)
    if not success:
        return render(request, 'usuario/password_change.html', {
            'form': form,
            'error': message
        })
    
    update_session_auth_hash(request, request.user)

    return render(request, 'usuario/password_change.html', {
        'form': PasswordChangeForm(),  # Limpia el formulario
        'success': message  # Muestra el modal
    })
