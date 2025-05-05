from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from core.forms.empleado_form import EmpleadoForm
from core.services.empleado_service import crear_empleado, get_all_empleados
from django.views.decorators.http import require_http_methods
from django.contrib import messages
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
                if modo == 'editar':
                    # Guardar directamente ya que el instance está establecido
                    form.save()
                    messages.success(
                        request, f'Empleado {"editado" if modo == "editar" else "creado"} exitosamente.')
                    return redirect('empleado_list')
                
            except Exception as e:
                print(f"Error al guardar: {str(e)}")  # Depuración
                messages.error(request, f'Error: {str(e)}')
        else:
            print("Errores del formulario:", form.errors)
    else:
        form = EmpleadoForm(instance=empleado)

    return render(request, 'empleado/empleado_form.html', {
        'form': form,
        'modo': modo,
        'empleado': empleado,
    })
