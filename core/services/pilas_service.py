from django.core.paginator import Paginator
from core.models.pilas import Pilas

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

def create_pila(form_data):
    """
    Create a new pila.
    
    Args:
        form_data: Validated form data
        
    Returns:
        Newly created pila object
    """
    return form_data.save()