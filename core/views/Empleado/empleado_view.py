from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from core.forms.empleado_form import EmpleadoForm
from core.services.empleado_service import crear_empleado, get_all_empleados

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

def empleado_create_view(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            crear_empleado(form)
            return redirect('empleado_list')
    else:
        form = EmpleadoForm()

    return render(request, 'empleado/empleado_form.html', {
        'form': form
    })
