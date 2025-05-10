from django.urls import path
from core.views.Reloj.reloj_view import reloj_list_view, reloj_create_view

urlpatterns = [
    path('servicios/reloj/', reloj_list_view, name='reloj_list'),
    path('servicios/reloj/agregar', reloj_create_view, name='reloj_create'),
]