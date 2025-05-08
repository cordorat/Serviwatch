from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from core.forms.recuperar_contraseña_form import RecuperarContrasenaForm
from core.forms.recuperar_contraseña_form import CambiarContrasenaForm
from core.services.recuperar_service import (
    get_user_by_username, is_email_matching,
    generate_password_reset_token, build_reset_url,
    send_password_reset_email, get_token,
    update_user_password, mark_token_as_used
)
from django.views.decorators.http import require_http_methods

url_recuperar_contrasenia = 'login/recuperar_contraseña.html'
url_cambiar_contrasenia = 'login/cambiar_contraseña.html'

@require_http_methods(["GET", "POST"])
def recuperar_contrasenia(request):
    if request.method == 'GET':
        return render(request, url_recuperar_contrasenia, {
            'form': RecuperarContrasenaForm(),
        })

    form = RecuperarContrasenaForm(request.POST)
    if not form.is_valid():
        return render(request, url_recuperar_contrasenia, {
            'form': form,
            'error': 'Formulario inválido'
        })

    usuario = request.POST.get('usuario', '')
    email = request.POST.get('email', '')

    user, error = get_user_by_username(usuario)
    if error:
        return render(request, url_recuperar_contrasenia, {
            'form': RecuperarContrasenaForm(),
            'error': error
        })

    if not is_email_matching(user, email):
        return render(request, url_recuperar_contrasenia, {
            'form': RecuperarContrasenaForm(),
            'error': 'El correo no está asociado a este usuario'
        })

    token = generate_password_reset_token(user)
    reset_url = build_reset_url(request, token)
    send_password_reset_email(email, reset_url)

    return render(request, url_recuperar_contrasenia, {
        'form': RecuperarContrasenaForm(),
        'success': 'Se ha enviado un enlace a tu correo para cambiar la contraseña'
    })

def cambiar_contrasenia(request, token):
    token_obj, error = get_token(token)
    if error == 'Token inválido':
        return render(request, 'login/token_invalido.html')
    if error == 'Token expirado':
        return render(request, 'login/token_expirado.html')

    user = token_obj.user

    if request.method == 'POST':
        form = CambiarContrasenaForm(request.POST)
        if form.is_valid():
            update_user_password(user, form.cleaned_data['password'])
            mark_token_as_used(token_obj)
            return render(request, url_cambiar_contrasenia, {
                'form': CambiarContrasenaForm(),
                'token': token,
                'success': '¡Tu contraseña ha sido actualizada correctamente!'
            })
        else:
            return render(request, url_cambiar_contrasenia, {
                'form': form,
                'token': token,
                'error': 'Formulario inválido. Verifica los campos.'
            })

    return render(request, url_cambiar_contrasenia, {
        'form': CambiarContrasenaForm(),
        'token': token
    })
