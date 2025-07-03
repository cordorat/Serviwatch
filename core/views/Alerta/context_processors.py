from django.utils import timezone
from datetime import timedelta
from core.models.reparacion import Reparacion
from core.models.pilas import Pilas

def alertas_processor(request):
    """Context processor para tener los contadores de alertas en todas las vistas"""
    if not request.user.is_authenticated:
        return {}
    
    fecha_actual = timezone.now().date()
    
    # Próximas entregas (reparaciones con fecha de entrega en menos de 7 días)
    contador_entregas = Reparacion.objects.filter(
        fecha_entrega_estimada__lte=fecha_actual + timedelta(days=7),
        fecha_entrega_estimada__gte=fecha_actual,
        estado__in=['Cotización', 'Reparación', 'Prueba', 'Listo']
    ).count()
    
    # Stock bajo (pilas con menos de 5 unidades)
    contador_stock = Pilas.objects.filter(cantidad__lt=5).count()
    
    # Próximas revisiones (reparaciones en prueba por más de 3 días)
    contador_revision = Reparacion.objects.filter(
        estado='Prueba',
        fecha_ingreso__lte=fecha_actual - timedelta(days=3)
    ).count()
    
    # Total de alertas
    total_alertas = contador_entregas + contador_stock + contador_revision
    
    return {
        'contador_entregas': contador_entregas,
        'contador_stock': contador_stock,
        'contador_revision': contador_revision,
        'total_alertas': total_alertas
    }