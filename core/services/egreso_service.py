from core.models.egreso import Egreso
from django.db import transaction

def crear_egreso(form):
    """
    Crea un nuevo egreso a partir del formulario
    """
    with transaction.atomic():
        egreso = form.save()
    return egreso

def get_all_egresos(fecha_inicio=None, fecha_fin=None, busqueda=None):
    """
    Obtiene todos los egresos con filtros opcionales
    """
    egresos = Egreso.objects.all()
    
    if fecha_inicio:
        egresos = egresos.filter(fecha__gte=fecha_inicio)
    
    if fecha_fin:
        egresos = egresos.filter(fecha__lte=fecha_fin)
    
    if busqueda:
        egresos = egresos.filter(descripcion__icontains=busqueda)
    
    return egresos.order_by('-fecha')

def crear_egreso_from_data(valor, fecha, descripcion):
    """
    Crea un nuevo egreso a partir de datos
    """
    with transaction.atomic():
        egreso = Egreso(
            valor=valor,
            fecha=fecha,
            descripcion=descripcion
        )
        egreso.save()
    return egreso