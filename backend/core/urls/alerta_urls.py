from django.urls import path
from core.views.Alerta.alerta_view import alerta_view

urlpatterns = [
    path('alertas/', alerta_view, name='alertas'),
]