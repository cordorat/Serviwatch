from django.urls import path
from core.views.Cliente.cliente_view import cliente_create_view, cliente_list_view

urlpatterns = [
    path('clientes/', cliente_list_view, name='cliente_list'),
    path('clientes/agregar/', cliente_create_view, name='cliente_create'),
    path('clientes/editar/<int:id>', cliente_create_view, name='cliente_editar'),
]