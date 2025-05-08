from django.urls import path
from core.views.Empleado.empleado_view import empleado_create_view, empleado_list_view

urlpatterns = [
    path('empleados/', empleado_list_view, name='empleado_list'),
    path('empleados/agregar/', empleado_create_view, name='empleado_create'),
    path('empleados/editar/<int:id>/', empleado_create_view, name='empleado_update'),
]
