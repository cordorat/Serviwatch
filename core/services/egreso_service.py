from core.models.egreso import Egreso
from django.db.models import Sum
from datetime import date
from django.core.exceptions import ValidationError
from django.db.utils import DatabaseError

def crear_egreso(datos):
    """
    Crea y guarda un nuevo registro de egreso en la base de datos.
    
    Args:
        datos (dict): Diccionario con los datos del egreso (fecha, valor, descripcion)
        
    Returns:
        Egreso: Instancia del modelo Egreso creado
    
    Raises:
        ValidationError: Si los datos no son válidos o hay problemas con la base de datos
    """
    try:
        # Verificar que todos los datos necesarios estén presentes
        required_keys = ['fecha', 'valor', 'descripcion']
        for key in required_keys:
            if key not in datos:
                raise ValidationError(f"Falta el dato requerido: {key}")

        # Crear una instancia de Egreso
        egreso = Egreso(
            fecha=datos['fecha'],
            valor=datos['valor'],
            descripcion=datos['descripcion']
        )
        # Guardar el egreso en la base de datos
        egreso.save()
        return egreso

    except ValidationError as ve:
        # Manejar errores de validación
        raise ve
    except Exception as e:
        # Manejar cualquier otro tipo de error
        raise DatabaseError(f"Error al crear el egreso: {str(e)}")
    
    
def obtener_total_egresos_dia(fecha=None):
    """
    Obtiene todos los egresos registrados en una fecha específica.
    Si no se proporciona fecha, usa la fecha actual.
    """
    if fecha is None:
        fecha = date.today()

    total = Egreso.objects.filter(fecha=fecha).aggregate(total=Sum('valor'))['total']
    return total or 0



"""
def obtener_egresos_rango(fecha_inicio, fecha_fin):

    Retorna una lista de egresos dentro del rango de fechas especificado (inclusive).

    Args:
        fecha_inicio (date): Fecha de inicio del rango.
        fecha_fin (date): Fecha final del rango.

    Returns:
        QuerySet: Lista de egresos en ese periodo, ordenados por fecha.

    return Egreso.objects.filter(
        fecha__range=(fecha_inicio, fecha_fin)
    ).order_by('fecha')


from django.db.models import Sum

def obtener_total_egresos_rango(fecha_inicio, fecha_fin):

    Calcula la suma total de egresos en un rango de fechas.

    Args:
        fecha_inicio (date): Fecha inicial del rango.
        fecha_fin (date): Fecha final del rango.

    Returns:
        Decimal: Total acumulado de egresos en ese período.

    total = Egreso.objects.filter(
        fecha__range=(fecha_inicio, fecha_fin)
    ).aggregate(total=Sum('valor'))['total']
    return total or 0    
"""