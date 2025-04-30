from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.forms.egreso_form import EgresoForm
from core.services.egreso_service import crear_egreso, crear_egreso_from_data, get_all_egresos
from django.views.decorators.http import require_http_methods
from datetime import datetime

@login_required
def egreso_list_view(request):
    """
    Vista para listar los egresos
    """
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    busqueda = request.GET.get('busqueda')
    
    egresos = get_all_egresos(fecha_inicio, fecha_fin, busqueda)
    return render(request, 'egreso/egreso_list.html', {'egresos': egresos})

@login_required
@require_http_methods(["GET", "POST"])
def egreso_view(request):
    """
    Vista para crear un nuevo egreso - Paso 1: Formulario
    """
    if request.method == 'POST':
        form = EgresoForm(request.POST)
        if form.is_valid():
            # Guardar datos en sesión para confirmar
            request.session['datos_egreso'] = {
                'valor': str(form.cleaned_data['valor']),
                'fecha_str': form.cleaned_data['fecha'].strftime('%Y-%m-%d'),
                'descripcion': form.cleaned_data['descripcion']
            }
            return redirect('confirmar_egreso')
    else:
        form = EgresoForm()
    
    return render(request, 'egreso/egreso_form.html', {'form': form})

@login_required
@require_http_methods(["GET", "POST"])
def confirmar_egreso_view(request):
    """
    Vista para confirmar la creación del egreso - Paso 2: Confirmación
    """
    # Obtener datos de la sesión
    datos_egreso = request.session.get('datos_egreso')
    
    # Si no hay datos, redirigir al formulario
    if not datos_egreso:
        messages.error(request, 'No hay datos para confirmar')
        return redirect('egreso')
    
    # Preparar datos para mostrar
    fecha = datetime.strptime(datos_egreso['fecha_str'], '%Y-%m-%d').date()
    datos_mostrar = {
        'valor': datos_egreso['valor'],
        'fecha': fecha.strftime('%d/%m/%Y'),
        'descripcion': datos_egreso['descripcion']
    }
    
    # Si es POST, procesar según la acción
    if request.method == 'POST':
        if 'confirmar' in request.POST:
            try:
                # Crear el egreso usando el servicio
                crear_egreso_from_data(
                    datos_egreso['valor'],
                    fecha,
                    datos_egreso['descripcion']
                )
                
                # Limpiar sesión
                if 'datos_egreso' in request.session:
                    del request.session['datos_egreso']
                
                messages.success(request, 'Egreso agregado correctamente')
                return redirect('egreso_list')
            except Exception as e:
                messages.error(request, f'Error al crear el egreso: {str(e)}')
                return render(request, 'egreso/confirmar_egreso.html', {
                    'datos': datos_mostrar,
                    'error': str(e)
                })
        else:
            # Botón corregir - volver al formulario
            return redirect('egreso')
    
    # GET request
    return render(request, 'egreso/confirmar_egreso.html', {'datos': datos_mostrar})