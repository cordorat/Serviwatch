from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
from core.models import PasswordResetToken
from django.template.loader import render_to_string
from django.utils.html import strip_tags


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
    """
    Envía un email de recuperación de contraseña con formato HTML personalizado
    """
    subject = '🔒 Recuperación de contraseña - Serviwatch'
    
    # Crear contexto para el template
    context = {
        'reset_url': reset_url,
        'email': email,
        'company_name': 'Serviwatch',
        'company_address': 'Calle 25 Norte # 5 an -17',
        'company_phone': '555-1234',
        'expiry_hours': 24,
    }
    
    # Renderizar template HTML
    html_content = render_to_string('usuario/password_reset.html', context)
    text_content = strip_tags(html_content)  # Versión de texto plano
    
    # Crear email con HTML
    email_message = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email]
    )
    
    email_message.attach_alternative(html_content, "text/html")
    email_message.send(fail_silently=False)

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
