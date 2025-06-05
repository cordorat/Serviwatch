from django.urls import path
from core.views.Reloj.reloj_view import reloj_list_view, reloj_create_view, reloj_update_view, reloj_sell_view
from core.views.Reloj.abono_view import abono_create_view

urlpatterns = [
    path('productos/reloj/', reloj_list_view, name='reloj_list'),
    path('productos/reloj/agregar', reloj_create_view, name='reloj_create'),
    path('productos/reloj/<int:pk>/editar', reloj_update_view, name='reloj_edit'),
    path('servicios/reloj/', reloj_list_view, name='reloj_venta_list'),
    path('servicios/reloj/<int:pk>/vender', reloj_sell_view, name='reloj_venta'),
    path('productos-admin/reloj/', reloj_list_view, name='reloj_list_admin'),
    path('productos-admin/reloj/agregar', reloj_create_view, name='reloj_create_admin'),
    path('productos-admin/reloj/<int:pk>/editar', reloj_update_view, name='reloj_edit_admin'),
    path('servicios/reloj/<int:reloj_id>/registrar-abono', abono_create_view, name='reloj_abono_create'),
]