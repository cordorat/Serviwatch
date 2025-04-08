from django.urls import path
from core.views import ClienteListView, ClienteCreateView

urlpatterns = [
    path('clientes/', ClienteListView.as_view(), name='cliente_list'),
    path('clientes/nuevo/', ClienteCreateView.as_view(), name='cliente_create'),
]