from django.urls import path
from core.views.Pilas.pilas_view import pilas_list_view, pila_create_view
from core.views.Pilas.ventaPila_view import ventaPilas_list_view, ventaPila_view

urlpatterns = [
    path('productos/pilas/', pilas_list_view, name='pilas_list'),
    path('productos/agregar/', pila_create_view, name='pilas_form'),
    path('productos/editar/<int:id>', pila_create_view, name='pila_editar'),
    path('servicios/pilas/', ventaPilas_list_view, name='ventaPila_list'),
    path('servicios/pilas/venta/', ventaPila_view, name='ventaPila_create'),
]