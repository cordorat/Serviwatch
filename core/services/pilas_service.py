from django.core.paginator import Paginator
from core.models.pilas import Pilas
from django.core.exceptions import ValidationError
from django.db import IntegrityError, DatabaseError

def get_pilas_paginated(page_number=1, items_per_page=6):
    """
    Get all pilas with pagination.
    
    Args:
        page_number: The requested page number
        items_per_page: Number of items per page
        
    Returns:
        Paginated pilas objects
    """
    pilas_list = Pilas.objects.all().order_by('codigo')
    paginator = Paginator(pilas_list, items_per_page)
    return paginator.get_page(page_number)

def create_pila(form):
    """
    Create a new pila.
    
    Args:
        form_data: Validated form data
        
    Returns:
        Newly created pila object
    """
    try:
        # Si el formulario tiene una instancia, es una edición
        pila = form.save()
        return pila
    except IntegrityError as e:
        # Errores de integridad (código duplicado, restricciones FK)
        raise ValidationError(f"Error de integridad al guardar la pila: {str(e)}")
    except DatabaseError as e:
        # Errores generales de base de datos
        raise ValidationError(f"Error de base de datos al guardar la pila: {str(e)}")
    except (ValueError, TypeError) as e:
        # Errores de validación de datos
        raise ValidationError(f"Error en los datos de la pila: {str(e)}")
    

def update_pila_stock_venta(pila_id, cantidad_venta):
    """
    Actualiza el stock de una pila después de una venta
    
    Args:
        pila_id: ID de la pila a actualizar
        cantidad_venta: Cantidad vendida (a restar del stock)
    """
    
    pila = Pilas.objects.get(id=pila_id)
    # Convertir a entero si es una cadena
    if isinstance(cantidad_venta, str):
        cantidad_venta = int(cantidad_venta)
    
    # Convertir cantidad actual a entero
    cantidad_actual = int(pila.cantidad)
    
    # Actualizar cantidad (restar la cantidad vendida)
    pila.cantidad = str(cantidad_actual - cantidad_venta)
    pila.save()
    
    return pila