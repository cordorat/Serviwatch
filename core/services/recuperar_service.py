from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from core.models import PasswordResetToken


def get_user_by_username(username):
    try:
        return get_user_model().objects.get(username=username), None
    except get_user_model().DoesNotExist:
        return None, "Usuario inexistente"


def is_email_matching(user, email):
    return user.email == email


def generate_password_reset_token(user):
    token = get_random_string(length=32)
    PasswordResetToken.objects.create(user=user, token=token)
    return token


def build_reset_url(request, token):
    return request.build_absolute_uri(reverse('cambiar_contraseña', kwargs={'token': token}))


def send_password_reset_email(email, reset_url):
    send_mail(
        subject='Recuperación de contraseña',
        message=f'Haz clic en el siguiente enlace para cambiar tu contraseña: {reset_url}\nEste enlace expirará en 24 horas.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


def get_token(token):
    try:
        token_obj = PasswordResetToken.objects.get(token=token)
        if not token_obj.is_valid():
            return None, 'Token expirado'
        return token_obj, None
    except PasswordResetToken.DoesNotExist:
        return None, 'Token inválido'


def update_user_password(user, password):
    user.set_password(password)
    user.save()


def mark_token_as_used(token_obj):
    token_obj.used = True
    token_obj.save()
