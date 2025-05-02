from django.shortcuts import render, redirect, get_object_or_404
from core.forms.cliente_form import ClienteForm
from core.services.cliente_service import get_all_clientes, crear_cliente
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q
from core.models.cliente import Cliente
from django.core.paginator import Paginator




@login_required
@require_http_methods(["GET"])
def cliente_list_view(request):
    clientes = get_all_clientes()

    paginator = Paginator(clientes, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'clientes': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }

    return render(request, "cliente/cliente_list.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def cliente_create_view(request, nombre=None, apellido=None, telefono=None):
    if nombre and apellido and telefono:
        cliente = get_object_or_404(Cliente, nombre=nombre, apellido=apellido, telefono=telefono)
        modo = 'editar'
    else:
        modo = 'agregar'
        cliente = None

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            crear_cliente(form)
            if modo == 'editar':
                messages.success(request, 'Cliente editado exitosamente.')
            else:
                messages.success(request, 'Cliente creado exitosamente.')
            form.save()
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)

            return redirect('cliente_list')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'cliente/cliente_form.html', {
        'form': form,
        'modo': modo
        })


def cliente_search_view(request):
    """Vista para búsqueda de clientes vía AJAX"""
    search_term = request.GET.get('term', '')
    print(f"Término de búsqueda recibido: {search_term}")  # Debug

    # Validar término de búsqueda
    if len(search_term) < 2:
        return JsonResponse([], safe=False)

    # Buscar clientes que coincidan
    clientes = Cliente.objects.filter(
        Q(nombre__icontains=search_term) | 
        Q(apellido__icontains=search_term) |
        Q(telefono__icontains=search_term)
    )[:10]
    

    # Formatear resultados
    results = []
    for cliente in clientes:
        results.append({
            'id': cliente.id,
            'label': f"{cliente.nombre} {cliente.apellido} - {cliente.telefono}",
            'value': f"{cliente.nombre} {cliente.apellido}",
            'telefono': cliente.telefono
        })

    print(f"Resultados encontrados: {results}")  # Debug
    return JsonResponse(results, safe=False)
