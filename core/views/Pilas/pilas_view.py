from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from core.forms.pila_form import PilasForm
from core.services.pilas_service import get_pilas_paginated, create_pila
from core.models.pilas import Pilas


@login_required
@require_http_methods(["GET"])
def pilas_list_view(request):
    """Vista para listar pilas con paginación"""
    # Use the service to get paginated pilas
    page_number = request.GET.get('page')
    pilas = get_pilas_paginated(page_number)
    
    context = {
        'pilas': pilas,
    }
    return render(request, 'pilas/pilas_list.html', context)


@login_required
def pila_create_view(request, id=None):
    """Vista para crear o editar pilas"""
    # Determinar modo y obtener instancia si es edición
    if id:
        pila = get_object_or_404(Pilas, id=id)
        modo = 'editar'
    else:
        modo = 'agregar'
        pila = None
    
    if request.method == 'POST':
        return _handle_post_request(request, pila, modo)
    else:
        return _handle_get_request(request, pila, modo)


def _handle_post_request(request, pila, modo):
    """Maneja las peticiones POST para crear/editar pilas"""
    form = PilasForm(request.POST, instance=pila)
    
    if form.is_valid():
        return _process_valid_form(request, form, modo)
    else:
        # Formulario inválido
        messages.error(request, 'Error al procesar el formulario. Por favor, corrige los errores.')
        return _render_form(request, form, modo)


def _process_valid_form(request, form, modo):
    """Procesa un formulario válido intentando guardarlo"""
    try:
        pila_guardada = create_pila(form)
        
        # Mensaje de éxito según el modo
        if modo == 'editar':
            messages.success(request, 'Referencia de pila editada con exito.')
        else:
            messages.success(request, 'Referencia de pila agregada con éxito')
        
        return redirect('pilas_list')
        
    except Exception as e:
        # Manejo de excepciones del servicio
        messages.error(request, f'Error al guardar la pila: {str(e)}')
        return _render_form(request, form, modo)


def _handle_get_request(request, pila, modo):
    """Maneja las peticiones GET para mostrar el formulario"""
    form = PilasForm(instance=pila)
    return _render_form(request, form, modo)


def _render_form(request, form, modo):
    """Renderiza el formulario de pila"""
    context = {
        'form': form,
        'modo': modo,
    }
    return render(request, 'pilas/pila_form.html', context)