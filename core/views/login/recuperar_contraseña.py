from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from core.forms.recuperar_contraseña_form import recuperarContrasenaForm
from core.forms.recuperar_contraseña_form import CambiarContrasenaForm
from core.models.cambiar_contraseña import PasswordResetToken

def recuperar_contraseña(request):
    if request.method == 'GET':
        return render(request, 'login/recuperar_contraseña.html', {
            'form': recuperarContrasenaForm(),
        })
    else:
        form = recuperarContrasenaForm(request.POST)
        if form.is_valid():
            usuario = request.POST.get('usuario', '')
            email = request.POST.get('email', '')

            print(usuario)
            print(email)

            try:
                user = get_user_model().objects.get(username=usuario)
            except get_user_model().DoesNotExist:
                return render(request, 'login/recuperar_contraseña.html', {
                    'form': recuperarContrasenaForm(),
                    'error': 'Usuario inexistente'
                })
            if user.email != email:
                return render(request, 'login/recuperar_contraseña.html', {
                    'form': recuperarContrasenaForm(),
                    'error': 'El correo no está asociado a este usuario'
                })
            else:
                # Generar token único para el cambio de contraseña
                token = get_random_string(length=32)
                
                # Guardar el token en el modelo separado
                reset_token = PasswordResetToken.objects.create(
                    user=user,
                    token=token
                )
                
                # Crear la URL para el cambio de contraseña
                reset_url = request.build_absolute_uri(
                    reverse('cambiar_contraseña', kwargs={'token': token})
                )
                
                # Enviar correo con el enlace para cambiar la contraseña
                send_mail(
                    subject='Recuperación de contraseña',
                    message=f'Haz clic en el siguiente enlace para cambiar tu contraseña: {reset_url}\n'
                           f'Este enlace expirará en 24 horas.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                return render(request, 'login/recuperar_contraseña.html', {
                    'form': recuperarContrasenaForm(),
                    'success': 'Se ha enviado un enlace a tu correo para cambiar la contraseña'
                })
        else: 
            return render(request, 'login/recuperar_contraseña.html', {
                'form': recuperarContrasenaForm(),
                'error': 'formulario invalido'
            })




def cambiar_contraseña(request, token):
    # Verificar si el token existe y no ha expirado
    try:
        reset_token = PasswordResetToken.objects.get(token=token)

        if not reset_token.is_valid():
            return render(request, 'login/token_expirado.html')

    except PasswordResetToken.DoesNotExist:
        return render(request, 'login/token_invalido.html')

    user = reset_token.user

    if request.method == 'POST':
        form = CambiarContrasenaForm(request.POST)
        if form.is_valid():
            # Cambiar la contraseña
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()

            # Marcar el token como usado
            reset_token.used = True
            reset_token.save()

            return render(request, 'login/cambiar_contraseña.html', {
                'form': CambiarContrasenaForm(),
                'token': token,
                'success': '¡Tu contraseña ha sido actualizada correctamente!'
            })
        else:
            return render(request, 'login/cambiar_contraseña.html', {
                'form': form,
                'token': token,
                'error': 'Formulario inválido. Verifica los campos.'
            })
    else:
        form = CambiarContrasenaForm()

    return render(request, 'login/cambiar_contraseña.html', {
        'form': form,
        'token': token
    })