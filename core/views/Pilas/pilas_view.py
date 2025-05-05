from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from core.forms.pila_form import PilasForm
from core.services.pilas_service import get_pilas_paginated, create_pila

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
def pila_create_view(request):
    if request.method == 'POST':
        form = PilasForm(request.POST)
        if form.is_valid():
            # Use the service to create a pila
            create_pila(form)
            messages.success(request, 'Referencia de pila agregada con éxito')
            return redirect('pilas_list')
    else:
        form = PilasForm()
    
    context = {
        'form': form,
    }
    return render(request, 'pilas/pila_form.html', context)