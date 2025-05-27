from django.shortcuts import render
from django.core.paginator import Paginator
from core.forms.empleado_form import EmpleadoForm
from core.services.empleado_service import _initialize_empleado, _handle_form_success, _handle_form_error
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from core.models.empleado import Empleado

@require_http_methods(["GET"])
def empleado_list_view(request,):
    filtro_estado = request.GET.get('estado', '')
    search_query = request.GET.get('search', '')

    empleados_qs = Empleado.objects.all()

    if filtro_estado and filtro_estado != 'todos':
        empleados_qs = empleados_qs.filter(estado=filtro_estado)

    if search_query:
        empleados_qs = empleados_qs.filter(
            Q(cedula__icontains=search_query) |
            Q(nombre__icontains=search_query) |
            Q(apellidos__icontains=search_query)
        )

    empleados_qs = empleados_qs.order_by('estado')

    paginator = Paginator(empleados_qs, 6)  # 6 registros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'empleado/empleado_list.html', {
        'page_obj': page_obj,
        'empleados': page_obj,  # Agregar esta línea
        # Para que la paginación funcione en el template
        'is_paginated': bool(empleados_qs),
        'filtro_estado': filtro_estado,
        'search': search_query,
        'estados': [('todos', 'Todos')] + list(Empleado.ESTADO_CHOICES),
    })


@require_http_methods(["POST", "GET"])
def empleado_create_view(request, id=None):
    # Inicializar empleado y modo
    empleado, modo = _initialize_empleado(id)
    
    # Para solicitudes GET
    if request.method == 'GET':
        form = EmpleadoForm(instance=empleado)
        success = request.GET.get('success') == 'true'
        return render(request, 'empleado/empleado_form.html', {
            'form': form, 'modo': modo, 'empleado': empleado, 'success': success
        })
    
    # Para solicitudes POST
    form = EmpleadoForm(request.POST, instance=empleado)
    
    # Si el formulario no es válido
    if not form.is_valid():
        error_response = _handle_form_error(request, "Formulario inválido", form)
        if error_response:
            return error_response
        return render(request, 'empleado/empleado_form.html', {
            'form': form, 'modo': modo, 'empleado': empleado
        })
    
    # Si el formulario es válido
    try:
        empleado = form.save()
        return _handle_form_success(request, empleado, modo)
    except Exception as e:
        error_response = _handle_form_error(request, str(e))
        if error_response:
            return error_response
        return render(request, 'empleado/empleado_form.html', {
            'form': form, 'modo': modo, 'empleado': empleado
        })