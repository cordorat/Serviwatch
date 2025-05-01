from django.urls import path
from core.views.Usuario.usuario_view import usuario_list_view, usuario_create_view

urlpatterns = [
    path('usuarios/', usuario_list_view, name='usuario_list'),
    path('usuarios/agregar/', usuario_create_view, name='usuario_create'),
]