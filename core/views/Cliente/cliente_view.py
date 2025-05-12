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
    
    clientes = clientes.order_by('nombre', 'apellido', 'telefono')

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
def cliente_create_view(request, id=None):
    if id:
        cliente = get_object_or_404(Cliente, id=id)
        modo = 'editar'
    else:
        modo = 'agregar'
        cliente = None

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente_obj = form.save()
            crear_cliente(form)
            
            # Manejar solicitudes AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Cliente editado exitosamente.' if modo == 'editar' else 'Cliente creado exitosamente.'
                })
                
            # Para solicitudes normales
            if modo == 'editar':
                messages.success(request, 'Cliente editado exitosamente.')
            else:
                messages.success(request, 'Cliente creado exitosamente.')
            
            # Si hay una URL de redirección especificada
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            
            # No redirigimos por defecto, dejamos que el cliente maneje la navegación
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

    # Inicializar la consulta base
    query = Q(nombre__icontains=search_term) | Q(apellido__icontains=search_term) | Q(telefono__icontains=search_term)
    
    # Búsqueda más específica si hay múltiples términos
    terms = search_term.split()
    if len(terms) >= 2:
        # Primer término como nombre, resto como apellido
        nombre_query = Q(nombre__icontains=terms[0])
        apellido_query = Q(apellido__icontains=' '.join(terms[1:]))
        query |= nombre_query & apellido_query
        
        # Último término como apellido, resto como nombre
        nombre_query2 = Q(nombre__icontains=' '.join(terms[:-1]))
        apellido_query2 = Q(apellido__icontains=terms[-1])
        query |= nombre_query2 & apellido_query2
    
    # Ejecutar la consulta
    clientes = Cliente.objects.filter(query)[:10]

    # Formatear resultados
    results = []
    for cliente in clientes:
        results.append({
            'id': cliente.id,
            'label': f"{cliente.nombre} {cliente.apellido} - {cliente.telefono}",
            'value': f"{cliente.nombre} {cliente.apellido}",
            'nombre': cliente.nombre,
            'apellido': cliente.apellido,
            'telefono': cliente.telefono
        })

    print(f"Resultados encontrados: {results}")  # Debug
    return JsonResponse(results, safe=False)
