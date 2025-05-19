from django.shortcuts import render, redirect
from core.forms.cliente_form import ClienteForm
from core.services.cliente_service import get_all_clientes, crear_cliente, _initialize_cliente, _handle_ajax_response, _add_success_message, _render_cliente_form
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator

@login_required
@require_http_methods(["GET"])
def cliente_list_view(request):
    clientes = get_all_clientes()
    search_term = request.GET.get('term', '')
    
    if search_term:
        # Realizar búsqueda si se proporciona un término
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
        
        clientes = clientes.filter(query)
    
    clientes = clientes.order_by('nombre', 'apellido', 'telefono')

    # Obtener todos los clientes para el datalist de autocompletado
    all_clientes = get_all_clientes().order_by('nombre', 'apellido')[:100]  # Limitamos a 100 para no sobrecargar

    paginator = Paginator(clientes, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'clientes': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_term': search_term,  # Devolvemos el término de búsqueda para mantenerlo en el formulario
        'all_clientes': all_clientes,  # Para el datalist de autocompletado
        'no_results': len(clientes) == 0 and search_term != '',  # Para mostrar el mensaje de no resultados
    }

    return render(request, "cliente/cliente_list.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def cliente_create_view(request, id=None):
    # Inicializar cliente y modo
    cliente, modo = _initialize_cliente(id)
    
    # Para solicitudes GET, simplemente renderizamos el formulario
    if request.method == 'GET':
        form = ClienteForm(instance=cliente)
        return _render_cliente_form(request, form, modo)
    
    # Para solicitudes POST, procesamos el formulario
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            try:
                crear_cliente(form)
                return _handle_ajax_response(modo=modo)
            except Exception as e:
                # Si hay error al guardar (por ejemplo, por duplicado)
                errors = {'__all__': [str(e)]}
                if 'unique' in str(e).lower() or 'duplicate' in str(e).lower():
                    # Intentar determinar qué campo está duplicado
                    if 'telefono' in str(e).lower():
                        errors = {'telefono': ['Este número de teléfono ya está registrado para otro cliente.']}
                    else:
                        errors = {'__all__': ['Ya existe un cliente con estos datos.']}
                
                return JsonResponse({
                    'success': False,
                    'errors': errors,
                    'message': 'No se pudo guardar el cliente.'
                }, status=400)
        else:
            # Formulario inválido
            return _handle_ajax_response(form=form, success=False)
    
    # Guardar el cliente y manejar la respuesta
    crear_cliente(form)
    
    # Manejar solicitud AJAX o normal
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return _handle_ajax_response(modo)
    
    # Para solicitudes normales
    _add_success_message(request, modo)
    
    # Redirigir si hay una URL especificada
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    
    # Mostrar el formulario con el mensaje de éxito
    return _render_cliente_form(request, form, modo)