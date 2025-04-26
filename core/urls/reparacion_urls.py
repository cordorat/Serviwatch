from django.urls import path
from core.views.Reparacion.reparacion_view import reparacion_list_view

urlpatterns = [
    path('reparaciones/', reparacion_list_view, name='reparacion_list'),
]