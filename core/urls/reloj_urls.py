from django.urls import path
from core.views.Reloj.reloj_view import reloj_list_view, reloj_create_view

urlpatterns = [
    path('productos/reloj/', reloj_list_view, name='reloj_list'),
    path('productos/reloj/agregar', reloj_create_view, name='reloj_create'),
]