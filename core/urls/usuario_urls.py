from django.urls import path
from core.views.Usuario.usuario_view import usuario_list_view, usuario_create_view, usuario_update_view, usuario_delete_view

urlpatterns = [
    path('usuarios/', usuario_list_view, name='usuario_list'),
    path('usuarios/agregar/', usuario_create_view, name='usuario_create'),
    path('usuarios/editar/<int:pk>/', usuario_update_view, name='usuario_update'), 
    path('usuarios/eliminar/<int:pk>/', usuario_delete_view, name='usuario_delete'),
]