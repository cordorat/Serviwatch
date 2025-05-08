from core.models import Reparacion
from django.shortcuts import get_object_or_404

def get_all_reparaciones():
    return Reparacion.objects.all()

def crear_reparacion(form):
    return form.save()


def get_reparacion_by_id(id):
    """
    Obtiene una reparación por su ID.
    
    Args:
        id: ID de la reparación
        
    Returns:
        Reparacion: La reparación encontrada o None
    """
    try:
        return Reparacion.objects.get(pk=id)
    except Reparacion.DoesNotExist:
        return None

def actualizar_reparacion(form, reparacion_id):
    """
    Actualiza una reparación existente con los datos del formulario.
    
    Args:
        form: Formulario de reparación validado
        reparacion_id: ID de la reparación a actualizar
        
    Returns:
        Reparacion: La instancia de reparación actualizada
        
    Raises:
        ValueError: Si la reparación no existe
    """
    reparacion = get_object_or_404(Reparacion, pk=reparacion_id)
    return form.save()

"""

def eliminar_reparacion(reparacion_id):
    try:
        reparacion = Reparacion.objects.get(pk=reparacion_id)
        reparacion.delete()
        return True
    except Reparacion.DoesNotExist:
        return False
"""