from django.shortcuts import render, redirect
from core.forms.login_form import LoginForm
from core.services.login_service import validate_credentials, get_user, authenticate_user, login_user
from django.views.decorators.http import require_http_methods

url_login = 'login/login.html'

@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'GET':
        return render(request, url_login, {'form': LoginForm()})

    usuario = request.POST.get('usuario', '')
    contrasenia = request.POST.get('contrasenia', '')

    is_valid, error = validate_credentials(usuario, contrasenia)
    if not is_valid:
        return render(request, url_login, {
            'form': LoginForm(),
            'error': error,
            'usuario_error': not usuario,
            'contrasenia_error': not contrasenia
        })

    # Verificar existencia del usuario
    user, error = get_user(usuario)
    if error:
        return render(request, url_login, {
            'form': LoginForm(),
            'error': error
        })

    # Autenticar usuario
    user, error = authenticate_user(request, usuario, contrasenia)
    if error:
        return render(request, url_login, {
            'form': LoginForm(),
            'error': error
        })

    # Login y redirección
    redirect_url = login_user(request, user)
    return redirect(redirect_url)
