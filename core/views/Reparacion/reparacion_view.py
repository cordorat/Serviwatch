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
from core.utils.security import is_safe_url



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
    if request.method == 'POST':
        # Remove extra fields that aren't part of the model
        post_data = request.POST.copy()
        if 'cliente_nombre' in post_data:
            del post_data['cliente_nombre']
        if 'celular_cliente' in post_data:
            del post_data['celular_cliente']
        
        form = ReparacionForm(post_data)
        if form.is_valid():
            try:
                reparacion = form.save()
                messages.success(request, "Reparación agregada correctamente.")
                return redirect('reparacion_list')
            except Exception as e:
                messages.error(request, f"Error al guardar: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
    else:
        form = ReparacionForm()

    context = {
        'form': form,
        'clientes': Cliente.objects.all(),
        'tecnicos': Empleado.objects.filter(cargo='Técnico')
    }
    return render(request, 'reparacion/reparacion_form.html', context)