from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views.Cliente.cliente_viewset import ClienteViewSet
from core.views.Empleado.empleado_viewset import EmpleadoViewSet
from core.views.Pilas.pilas_viewset import PilasViewSet
from core.views.Pilas.venta_pila_viewset import VentaPilaViewSet
from core.views.Ingreso.ingreso_viewset import IngresoViewSet
from core.views.Egreso.egreso_viewset import EgresoViewSet
from core.views.Reloj.reloj_viewset import RelojViewSet
from core.views.Reloj.abono_viewset import AbonoViewSet
from core.views.Reparacion.reparacion_viewset import ReparacionViewSet

# Router de DRF - genera automáticamente las URLs para ViewSets
router = DefaultRouter()

# Registrar ViewSets
router.register(r'clientes', ClienteViewSet, basename='api-cliente')
router.register(r'empleados', EmpleadoViewSet, basename='api-empleado')
router.register(r'pilas', PilasViewSet, basename='api-pilas')
router.register(r'ventas-pilas', VentaPilaViewSet, basename='api-venta-pila')
router.register(r'ingresos', IngresoViewSet, basename='api-ingreso')
router.register(r'egresos', EgresoViewSet, basename='api-egreso')
router.register(r'relojes', RelojViewSet, basename='api-reloj')
router.register(r'abonos', AbonoViewSet, basename='api-abono')
router.register(r'reparaciones', ReparacionViewSet, basename='api-reparacion')

# URLs de la API
urlpatterns = [
    # Incluir todas las rutas del router
    path('', include(router.urls)),
]

# URLs generadas automáticamente por el router:
#
# CLIENTES:
# GET    /api/clientes/                    - Listar clientes (con paginación y búsqueda)
# POST   /api/clientes/                    - Crear cliente
# GET    /api/clientes/{id}/               - Obtener cliente específico
# PUT    /api/clientes/{id}/               - Actualizar cliente completo
# PATCH  /api/clientes/{id}/               - Actualizar cliente parcial
# DELETE /api/clientes/{id}/               - Eliminar cliente
# GET    /api/clientes/buscar/?term=xxx    - Buscar clientes
# GET    /api/clientes/autocompletado/?term=xxx - Autocompletado de clientes
#
# EMPLEADOS:
# GET    /api/empleados/                   - Listar empleados (con paginación y búsqueda)
# POST   /api/empleados/                   - Crear empleado
# GET    /api/empleados/{id}/              - Obtener empleado específico
# PUT    /api/empleados/{id}/              - Actualizar empleado completo
# PATCH  /api/empleados/{id}/              - Actualizar empleado parcial
# DELETE /api/empleados/{id}/              - Marcar empleado como inactivo
# GET    /api/empleados/buscar/?term=xxx   - Buscar empleados
# GET    /api/empleados/activos/           - Listar solo empleados activos
# GET    /api/empleados/tecnicos/          - Listar solo técnicos activos
# PATCH  /api/empleados/{id}/cambiar-estado/ - Cambiar estado Activo/Inactivo
# GET    /api/empleados/estadisticas/      - Estadísticas de empleados
