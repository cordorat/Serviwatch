from django.urls import path
from core.views.Reloj.reloj_view import reloj_list_view, reloj_create_view, reloj_update_view, reloj_sell_view, reporte_relojes_pdf
from core.views.Reloj.abono_view import abono_create_view

urlpatterns = [
    path('productos/reloj/', reloj_list_view, name='reloj_list'),
    path('productos/reloj/agregar', reloj_create_view, name='reloj_create'),
    path('productos/reloj/<int:pk>/editar', reloj_update_view, name='reloj_edit'),
    path('productos/reloj/reporte/', reporte_relojes_pdf, name='reporte_relojes_pdf'),
    path('servicios/reloj/', reloj_list_view, name='reloj_venta_list'),
    path('servicios/reloj/<int:pk>/vender', reloj_sell_view, name='reloj_venta'),
    path('servicios/reloj/reporte/', reporte_relojes_pdf, name='reporte_relojes_venta_pdf'),
    path('productos-admin/reloj/', reloj_list_view, name='reloj_list_admin'),
    path('productos-admin/reloj/agregar', reloj_create_view, name='reloj_create_admin'),
    path('productos-admin/reloj/<int:pk>/editar', reloj_update_view, name='reloj_edit_admin'),
    path('servicios/reloj/<int:reloj_id>/registrar-abono', abono_create_view, name='reloj_abono_create'),
]