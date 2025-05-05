from django.urls import path
from core.views.Usuario.usuario_view import usuario_list_view, usuario_create_view
from core.views.Usuario.password_change_view import password_change_view
urlpatterns = [
    path('usuarios/', usuario_list_view, name='usuario_list'),
    path('usuarios/agregar/', usuario_create_view, name='usuario_create'),
    path('cambiar-contraseña/', password_change_view, name='password_change'),
    ]