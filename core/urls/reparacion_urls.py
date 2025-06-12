from django.urls import path
from core.views.Reparacion.reparacion_view import reparacion_list_view, reparacion_create_view, reparacion_edit_view, reporte_reparaciones_pdf

urlpatterns = [
    path('servicios/reparaciones/', reparacion_list_view, name='reparacion_list'),
    path('servicios/reparaciones/agregar', reparacion_create_view, name='reparacion_create'),
    path('reparacion/edit/<int:pk>/', reparacion_edit_view, name='reparacion_edit'),
    path('reparaciones/reporte/', reporte_reparaciones_pdf, name='reporte_reparaciones_pdf'),
    path('productos-admin/reparaciones/', reparacion_list_view, name='reparacion_list_admin'),
]