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




@login_required
@require_http_methods(["GET"])
def reparacion_list_view(request):
    search_query = request.GET.get('search', '')
    
    if search_query:
        reparaciones_qs = Reparacion.objects.filter(
            Q(codigo_orden__icontains=search_query) |
            Q(cliente__nombre__icontains=search_query) |
            Q(cliente__telefono__icontains=search_query) |
            Q(tecnico__nombre__icontains=search_query) |
            Q(descripcion__icontains=search_query)
        ).order_by('estado')
    else:
        reparaciones_qs = Reparacion.objects.all().order_by('estado')
        
    paginator = Paginator(reparaciones_qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'reparaciones': page_obj,          # esto sigue funcionando si iteras sobre {{ reparaciones }}
        'page_obj': page_obj,              # necesario para el paginador
        'is_paginated': page_obj.has_other_pages(),
        'search': search_query,# activa el bloque de paginación en el template
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
    """Maneja las solicitudes POST para crear una reparación."""
    # Limpiar datos del formulario
    post_data = _clean_post_data(request.POST.copy())
    
    form = ReparacionForm(post_data)
    if form.is_valid():
        try:
            form.save()
            messages.success(request, "Reparación agregada correctamente.")
            return redirect('reparacion_list')
        except Exception as e:
            messages.error(request, f"Error al guardar: {str(e)}")
    else:
        _add_form_errors_to_messages(form, request)
    
    return _render_create_form(request, form)


def _handle_create_get(request):
    """Maneja las solicitudes GET para mostrar el formulario de creación."""
    form = ReparacionForm()
    return _render_create_form(request, form)


def _render_create_form(request, form):
    """Renderiza el formulario de creación con el contexto apropiado."""
    context = {
        'form': form,
        'clientes': Cliente.objects.all(),
        'tecnicos': Empleado.objects.filter(cargo='Técnico')
    }
    return render(request, 'reparacion/reparacion_form.html', context)

@login_required
def reparacion_edit_view(request, pk):
    # Intentar obtener la reparación
    reparacion = _get_reparacion_or_redirect(request, pk)  # Pasamos request aquí
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
            messages.success(request, "Reparación actualizada correctamente.")
            return redirect('reparacion_list')
        except Exception as e:
            messages.error(request, f"Error al actualizar: {str(e)}")
    else:
        _add_form_errors_to_messages(form, request)
    
    # Si llegamos aquí, hubo un error, mostrar el formulario nuevamente
    return _render_edit_form(request, form, reparacion)


def _handle_edit_get(request, reparacion):
    """Maneja las solicitudes GET para mostrar el formulario de edición."""
    form = ReparacionForm(instance=reparacion)
    return _render_edit_form(request, form, reparacion)


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


def _render_edit_form(request, form, reparacion):
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
        'cliente_telefono': cliente_telefono
    }
    return render(request, 'reparacion/reparacion_form.html', context)
