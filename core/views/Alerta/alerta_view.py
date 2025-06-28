from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from core.models.reparacion import Reparacion
from core.models.pilas import Pilas
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import Cast
from django.db.models import IntegerField


@login_required
@require_http_methods(["GET"])
def alerta_view(request):
    """Vista para mostrar las alertas del sistema como filtros en una única ventana"""
    tipo = request.GET.get('tipo', 'proxima_entrega')  # Por defecto muestra próximas entregas
    
    # Obtener la fecha actual
    fecha_actual = timezone.now().date()
    
    # Inicializar un QuerySet vacío
    items = []
    
    if tipo == 'proxima_entrega':
        # Filtrar reparaciones que vencen en menos de 7 días y no están entregadas
        fecha_limite = fecha_actual + timedelta(days=7)
        items = Reparacion.objects.filter(
            fecha_entrega_estimada__lte=fecha_limite,
            fecha_entrega_estimada__gte=fecha_actual,
            estado__in=['Cotización', 'Reparación', 'Prueba', 'Listo']  # Excluir entregados
        ).order_by('fecha_entrega_estimada')
        
    elif tipo == 'stock_bajo':
        # Pilas con stock bajo (menor o igual a 7 unidades)
        # Como cantidad es CharField, necesitamos filtrar en Python
        all_pilas = Pilas.objects.all()
        items = []
        for pila in all_pilas:
            try:
                cantidad_int = int(pila.cantidad)
                if cantidad_int <= 7:
                    items.append(pila)
            except ValueError:
                # Si no se puede convertir a entero, consideramos que tiene stock bajo
                items.append(pila)
        # Ordenar por cantidad (convertida a entero)
        items.sort(key=lambda p: int(p.cantidad) if p.cantidad.isdigit() else 0)
        
    elif tipo == 'proxima_revision':
        # Reparaciones con mantenimiento que han pasado más de 1 mes desde su ingreso
        # Consideramos que necesitan revisión después de 30 días de haber ingresado
        fecha_limite_revision = fecha_actual - timedelta(days=365*3)  # Hace 1 mes
        
        items = Reparacion.objects.filter(
            mantenimiento=True,
            estado='Entregado',  # Incluye entregadas
            fecha_ingreso__lte=fecha_limite_revision  # Ingresaron hace 1 mes o más
        ).order_by('fecha_ingreso')
    
    # Obtener contadores para los recuadros de categorías
    contador_entregas = Reparacion.objects.filter(
        fecha_entrega_estimada__lte=fecha_actual + timedelta(days=7),
        fecha_entrega_estimada__gte=fecha_actual,
        estado__in=['Cotización', 'Reparación', 'Prueba', 'Listo']
    ).count()
    
    # Calcular contador de stock bajo (cantidad <= 7)
    all_pilas_for_count = Pilas.objects.all()
    contador_stock = 0
    for pila in all_pilas_for_count:
        try:
            cantidad_int = int(pila.cantidad)
            if cantidad_int <= 7:
                contador_stock += 1
        except ValueError:
            # Si no se puede convertir, consideramos que tiene stock bajo
            contador_stock += 1
    
    # Actualizar también el contador_revision
    contador_revision = Reparacion.objects.filter(
        mantenimiento=True,
        estado='Entregado',
        fecha_ingreso__lte=fecha_actual - timedelta(days=365*3)  # Hace 1 mes o más
    ).count()
    
    # Paginación
    paginator = Paginator(items, 6)  # 6 elementos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tipo_actual': tipo,
        'items': page_obj,
        'page_obj': page_obj,
        'contador_entregas': contador_entregas,
        'contador_stock': contador_stock,
        'contador_revision': contador_revision,
        'total_alertas': contador_entregas + contador_stock + contador_revision
    }
    
    return render(request, 'alerta/alerta_list.html', context)