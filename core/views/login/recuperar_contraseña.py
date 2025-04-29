from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from core.forms.recuperar_contraseña_form import recuperarContrasenaForm


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
                send_mail(
                    subject='Recuperación de contraseña',
                    message=f'Tu contraseña es: {user.password}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                user.password_reset_required=True
                user.save()
                return render(request, 'login/recuperar_contraseña.html', {
                    'form': recuperarContrasenaForm(),
                    'success': 'Se le ha enviado la contraseña al correo registrado'
                })
        else: 
            return render(request, 'login/recuperar_contraseña.html', {
                'form': recuperarContrasenaForm(),
                'error': 'formulario invalido'
            })