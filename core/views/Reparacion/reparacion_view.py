from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.forms.reparacion_form import ReparacionForm
from core.models.reparacion import Reparacion
from django.views.decorators.http import require_http_methods
from core.models.cliente import Cliente
from core.models.empleado import Empleado
from django.core.paginator import Paginator
from django.db.models import Q
from core.services import reparacion_service
from django.db import models
from django.http import JsonResponse


@login_required
@require_http_methods(["GET"])
def reparacion_list_view(request):
    filtro_estado = request.GET.get('estado', '')
    search_query = request.GET.get('search', '')

    reparaciones_qs = Reparacion.objects.all()

    if filtro_estado and filtro_estado != 'todos':
        reparaciones_qs = reparaciones_qs.filter(estado=filtro_estado)

    if search_query:
        # Dividir la consulta en términos individuales
        search_terms = search_query.split()

        # Inicializar una consulta Q vacía
        query = Q()

        # Crear una consulta base que funcione con términos únicos
        base_query = (
            Q(codigo_orden__icontains=search_query) |
            Q(cliente__nombre__icontains=search_query) |
            Q(cliente__apellido__icontains=search_query) |
            Q(cliente__telefono__icontains=search_query) |
            Q(tecnico__nombre__icontains=search_query) |
            Q(tecnico__apellidos__icontains=search_query) 
        )
        query |= base_query

        # Si hay múltiples términos, buscar coincidencias de nombre+apellido
        if len(search_terms) > 1:
            for i in range(len(search_terms) - 1):
                # Buscar coincidencias donde términos consecutivos aparezcan en nombre+apellido
                first_term = search_terms[i]
                second_term = search_terms[i+1]

                # Buscar "nombre apellido"
                query |= (Q(cliente__nombre__icontains=first_term) &
                        Q(cliente__apellido__icontains=second_term))

                # También buscar posibles segundos nombres
                query |= (Q(cliente__nombre__icontains=first_term) &
                        Q(cliente__nombre__icontains=second_term))
                
                query |= (Q(tecnico__nombre__icontains=first_term) &
                        Q(tecnico__apellidos__icontains=second_term))

                # También buscar posibles segundos nombres
                query |= (Q(tecnico__nombre__icontains=first_term) &
                        Q(tecnico__nombre__icontains=second_term))

        reparaciones_qs = reparaciones_qs.filter(query).distinct()

    # Aplicar ordenamiento según el flujo de trabajo
    # Primero Cotización, luego Reparación, finalmente Listo
    order_mapping = {
        'Cotización': 1,
        'Reparación': 2,
        'Listo': 3
    }
    reparaciones_qs = reparaciones_qs.order_by(
        # Ordenar primero por el campo estado según el flujo de trabajo
        models.Case(
            *[models.When(estado=estado, then=models.Value(orden)) 
              for estado, orden in order_mapping.items()],
            default=models.Value(999),
            output_field=models.IntegerField()
        ),
        # Después por fecha de creación descendente (las más recientes primero)
        '-fecha_ingreso'
    )
    
    paginator = Paginator(reparaciones_qs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        # esto sigue funcionando si iteras sobre {{ reparaciones }}
        'reparaciones': page_obj,
        'page_obj': page_obj,              # necesario para el paginador
        'is_paginated': bool(reparaciones_qs),
        'search': search_query,  # activa el bloque de paginación en el template
        'filtro_estado': filtro_estado,
        'estados': [('todos', 'Todos')] + list(Reparacion.ESTADOS),
    }

    return render(request, 'reparacion/reparacion_list.html', context)


@login_required
def reparacion_create_view(request):
    """Vista para crear una nueva reparación."""
    if request.method == 'POST':
        return _handle_create_post(request)
    else:
        return _handle_create_get(request)


def _handle_create_post(request):
    # Limpiar datos del formulario
    post_data = _clean_post_data(request.POST.copy())
    
    form = ReparacionForm(post_data)
    if form.is_valid():
        try:
            reparacion = form.save()
            
            # Si es una solicitud AJAX, devolver respuesta JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': "Reparación agregada correctamente."
                })
                
            messages.success(request, "Reparación agregada correctamente.")
            return redirect('reparacion_list')
        except Exception as e:
            # Si es una solicitud AJAX, devolver error en JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Intentar determinar si es un error de integridad de BD (duplicado)
                if 'duplicate' in str(e).lower() or 'unique constraint' in str(e).lower():
                    return JsonResponse({
                        'success': False,
                        'errors': {
                            'codigo_orden': 'Este código de orden ya existe. Por favor, use otro.'
                        }
                    }, status=400)
                else:
                    return JsonResponse({
                        'success': False,
                        'message': str(e)
                    }, status=400)
                
            messages.error(request, f"Error al guardar: {str(e)}")
    else:
        # Si es una solicitud AJAX, devolver errores en JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {field: error[0] for field, error in form.errors.items()}
            return JsonResponse({
                'success': False,
                'errors': errors
            }, status=400)
            
        _add_form_errors_to_messages(form, request)

    # Verificar si debemos mostrar la página con el modal
    success = request.GET.get('success') == 'true'
    
    return _render_create_form(request, form, success)


def _handle_create_get(request):
    """Maneja las solicitudes GET para mostrar el formulario de creación."""
    form = ReparacionForm()
    
    # Verificar si debemos mostrar el modal de éxito
    success = request.GET.get('success') == 'true'
    
    return _render_create_form(request, form, success)


def _render_create_form(request, form, success=False):
    """Renderiza el formulario de creación con el contexto apropiado."""
    context = {
        'form': form,
        'clientes': Cliente.objects.all(),
        'tecnicos': Empleado.objects.filter(cargo='Técnico'),
        'success': success
    }
    return render(request, 'reparacion/reparacion_form.html', context)


@login_required
def reparacion_edit_view(request, pk):
    # Intentar obtener la reparación
    reparacion = _get_reparacion_or_redirect(
        request, pk)  # Pasamos request aquí
    if not isinstance(reparacion, Reparacion):
        # Si no es una reparación, significa que es una respuesta de redirección
        return reparacion

    if request.method == 'POST':
        return _handle_edit_post(request, reparacion, pk)
    else:
        return _handle_edit_get(request, reparacion)


def _get_reparacion_or_redirect(request, pk):
    """Obtiene la reparación o devuelve una redirección si no existe."""
    try:
        reparacion = reparacion_service.get_reparacion_by_id(pk)
        if not reparacion:
            messages.error(request, "La reparación no existe.")
            return redirect('reparacion_list')
        return reparacion
    except Exception as e:
        messages.error(request, f"Error inesperado: {str(e)}")
        return redirect('reparacion_list')


def _handle_edit_post(request, reparacion, pk):
    """Maneja las solicitudes POST para editar una reparación."""
    # Limpiar datos del formulario
    post_data = _clean_post_data(request.POST.copy())

    form = ReparacionForm(post_data, instance=reparacion)
    if form.is_valid():
        try:
            reparacion = reparacion_service.actualizar_reparacion(form, pk)
            
            # Si es una solicitud AJAX, devolver respuesta JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': "Reparación actualizada correctamente."
                })
            
            messages.success(request, "Reparación actualizada correctamente.")
            return redirect('reparacion_list')
        except Exception as e:
            # Si es una solicitud AJAX, devolver error en JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=400)
                
            messages.error(request, f"Error al actualizar: {str(e)}")
    else:
        # Si es una solicitud AJAX, devolver errores en JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {field: error[0] for field, error in form.errors.items()}
            return JsonResponse({
                'success': False,
                'errors': errors
            }, status=400)
            
        _add_form_errors_to_messages(form, request)

    # Verificar si debemos mostrar la página con el modal
    success = request.GET.get('success') == 'true'
    
    # Si llegamos aquí, hubo un error, mostrar el formulario nuevamente
    return _render_edit_form(request, form, reparacion, success)

def _handle_edit_get(request, reparacion):
    """Maneja las solicitudes GET para el formulario de edición."""
    form = ReparacionForm(instance=reparacion)
    
    # Verificar si debemos mostrar el modal de éxito
    success = request.GET.get('success') == 'true'
    
    return _render_edit_form(request, form, reparacion, success)


def _clean_post_data(post_data):
    """Elimina campos extra que no son parte del modelo."""
    if 'cliente_nombre' in post_data:
        del post_data['cliente_nombre']
    if 'celular_cliente' in post_data:
        del post_data['celular_cliente']
    return post_data


def _add_form_errors_to_messages(form, request):
    """Añade los errores del formulario a los mensajes."""
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f"Error en {field}: {error}")


def _render_edit_form(request, form, reparacion, success=False):
    """Renderiza el formulario de edición con el contexto apropiado."""
    # Prepara datos adicionales para el frontend
    cliente_actual = reparacion.cliente
    cliente_nombre = f"{cliente_actual.nombre}" if cliente_actual else ""
    cliente_telefono = cliente_actual.telefono if cliente_actual else ""

    context = {
        'form': form,
        'clientes': Cliente.objects.all(),
        'tecnicos': Empleado.objects.filter(cargo='Técnico'),
        'editing': True,
        'reparacion': reparacion,
        'cliente_nombre': cliente_nombre,
        'cliente_telefono': cliente_telefono,
        'success': success  # Asegurarse de que este parámetro se está pasando
    }
    return render(request, 'reparacion/reparacion_form.html', context)
