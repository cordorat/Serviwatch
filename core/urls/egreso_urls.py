from django.urls import path
from core.views.Egreso.egreso_view import egreso_view, confirmar_egreso_view, egreso_list_view

urlpatterns = [
    path('egreso/', egreso_view, name='egreso'),
    path('egreso/confirmar/', confirmar_egreso_view, name='confirmar_egreso'),
    path('egreso/listar/', egreso_list_view, name='egreso_list'),
]