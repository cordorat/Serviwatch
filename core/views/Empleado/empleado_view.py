from django.shortcuts import render
from django.core.paginator import Paginator
from core.forms.empleado_form import EmpleadoForm
from core.services.empleado_service import _initialize_empleado, _handle_form_success, _handle_form_error
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from core.models.empleado import Empleado
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages


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
    if id:
        empleado = get_object_or_404(Empleado, id=id)
        modo = 'editar'
    else:
        empleado = None
        modo = 'agregar'

    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        print("Datos del formulario:", request.POST)  # Depuración

        if form.is_valid():
            print("Formulario válido!")
            try:
                empleado = form.save()
                messages.success(
                    request, f'Empleado {"editado" if modo == "editar" else "creado"} exitosamente.')
                
                # Manejar solicitudes AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Empleado {"editado" if modo == "editar" else "creado"} exitosamente.'
                    })
                
                # Si hay una solicitud específica para mostrar el modal
                if request.headers.get('X-Show-Modal') == 'true':
                    return JsonResponse({
                        'success': True,
                        'redirect': f"{request.path}?success=true"
                    })
                
                # Para solicitudes normales
                return redirect('empleado_list')

            except Exception as e:
                print(f"Error al guardar: {str(e)}")  # Depuración
                messages.error(request, f'Error: {str(e)}')
                # Para solicitudes AJAX, devolver error en formato JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': str(e)
                    }, status=400)
                
        else:
            print("Errores del formulario:", form.errors)
            # Si es una solicitud AJAX, devolver errores en formato JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = {field: error[0] for field, error in form.errors.items()}
                return JsonResponse({
                    'success': False,
                    'errors': errors
                }, status=400)
                
    else:
        form = EmpleadoForm(instance=empleado)

    # Verificar si estamos mostrando el modal de éxito
    success = request.GET.get('success') == 'true'

    return render(request, 'empleado/empleado_form.html', {
        'form': form,
        'modo': modo,
        'empleado': empleado,
        'success': success
    })





@require_http_methods(["GET"])
def reporte_empleados_pdf(request):
    """
    Vista para generar un reporte PDF de empleados con los mismos filtros
    que se están usando en la vista de lista.
    """
    filtro_estado = request.GET.get('estado', '')
    search_query = request.GET.get('search', '')

    # Usar la misma lógica de filtrado que en empleado_list_view
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
    
    # Generar el PDF
    from core.services.empleado_service import generar_pdf_empleados
    pdf = generar_pdf_empleados(empleados_qs, filtro_estado, request)
    
    # Devolver el PDF como respuesta HTTP
    estado_texto = filtro_estado if filtro_estado and filtro_estado != 'todos' else 'todos'
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="reporte_empleados_{estado_texto}.pdf"'
    return response