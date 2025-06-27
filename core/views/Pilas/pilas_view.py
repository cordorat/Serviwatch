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
    # Use the service to get paginated pilas
    page_number = request.GET.get('page')
    pilas = get_pilas_paginated(page_number)
    
    context = {
        'pilas': pilas,
    }
    return render(request, 'pilas/pilas_list.html', context)

@login_required
def pila_create_view(request, id=None):
    if id:
        pila = get_object_or_404(Pilas, id=id)
        modo = 'editar'
    else:
        modo = 'agregar'
        pila = None
    if request.method == 'POST':
        form = PilasForm(request.POST, instance=pila)
        if form.is_valid():
            
            try:
                pila_guardada = create_pila(form)
            # Use the service to create a pila
                if modo == 'editar':
                    messages.success(request, 'Referencia de pila editada con exito.')
                else:
                    messages.success(request, 'Referencia de pila agregada con éxito')
                    
                return redirect('pilas_list')
            
            except Exception as e:
                messages.error(request, f'Error al guardar la pila: {str(e)}')
        else:
            messages.error(request, 'Error al procesar el formulario. Por favor, corrige los errores.')        
                
    else:
        form = PilasForm(instance=pila)
    
    context = {
        'form': form,'modo': modo,
    }
    return render(request, 'pilas/pila_form.html', context)