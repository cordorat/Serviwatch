from django.urls import path
from core.views.cliente_view import cliente_create_view, cliente_list_view

urlpatterns = [
    path('clientes/', cliente_list_view, name='cliente_list'),
    path('clientes/nuevo/', cliente_create_view, name='cliente_create'),
]