from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from core.forms.empleado_form import EmpleadoForm
from core.services.empleado_service import crear_empleado, get_all_empleados
from django.views.decorators.http import require_http_methods
from django.contrib import messages




@require_http_methods(["GET"])
def empleado_list_view(request):
    filtro_estado = request.GET.get('estado')
    busqueda_cedula = request.GET.get('cedula')
    empleados = get_all_empleados(filtro_estado, busqueda_cedula)

    paginator = Paginator(empleados, 6)  # 6 registros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'empleado/empleado_list.html', {
        'page_obj': page_obj,
        'filtro_estado': filtro_estado,
        'busqueda_cedula': busqueda_cedula,
    })


@require_http_methods(["POST", "GET"])
def empleado_create_view(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            try:
                crear_empleado(form)
                messages.success(request, 'Empleado creado exitosamente.')
                return redirect('empleado_list')
            except Exception as e:
                messages.error(request, f'Error al crear empleado: {str(e)}')
    else:
        form = EmpleadoForm()

    return render(request, 'empleado/empleado_form.html', {
        'form': form
    })
