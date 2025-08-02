from datetime import date
from django.shortcuts import render, redirect
from core.services.ingreso_service import obtener_total_ingresos_dia 
from core.forms.ingreso_form import IngresoForm
from django.contrib.auth.decorators import login_required


@login_required
def ingreso_view(request):
    total_ingresos = obtener_total_ingresos_dia()

    # Verificar si se debe limpiar la sesión (cuando se cancela)
    if request.GET.get('clear') == 'true':
        if 'ingreso_data' in request.session:
            del request.session['ingreso_data']
        if 'ingreso_from_form' in request.session:
            del request.session['ingreso_from_form']
        return redirect('ingreso')  # Redirigir sin parámetros para limpiar la URL

    if request.method == 'POST':
        form = IngresoForm(request.POST)
        if form.is_valid():
            # Solo pasar los datos limpios a la sesión, sin crear objeto
            request.session['ingreso_data'] = {
                'fecha': str(form.cleaned_data['fecha']),
                'valor': form.cleaned_data['valor'],
                'descripcion': form.cleaned_data['descripcion']
            }
            # Marcar que venimos del formulario para no limpiar en próxima visita
            request.session['ingreso_from_form'] = True
            return redirect('confirmar_ingreso')
        # Si el formulario NO es válido, se renderizará de nuevo con errores
    else:
        # Si hay datos en sesión, verificar si venimos de la confirmación o de navegación externa
        if 'ingreso_data' in request.session:
            # Si no venimos del formulario/confirmación, limpiar automáticamente
            if not request.session.get('ingreso_from_form', False):
                del request.session['ingreso_data']
                if 'ingreso_from_form' in request.session:
                    del request.session['ingreso_from_form']
                form = IngresoForm()
            else:
                # Venimos de "editar", mantener los datos y resetear la bandera
                request.session['ingreso_from_form'] = False
                from datetime import datetime
                datos = request.session['ingreso_data']
                
                # Convertir la fecha de string a date para el formulario
                # Por un manejo flexible de formatos:
                try:
                    # Intenta primero el formato previo
                    fecha = datetime.strptime(datos['fecha'], '%Y-%m-%d').date()
                except ValueError:
                    try:
                        # Intenta el formato con guiones
                        fecha = datetime.strptime(datos['fecha'], '%d-%m-%Y').date()
                    except ValueError:
                        # Intenta el formato con barras (Flatpickr)
                        fecha = datetime.strptime(datos['fecha'], '%d/%m/%Y').date()
                
                # Pre-poblar el formulario con los datos guardados
                form = IngresoForm(initial={
                    'fecha': fecha,
                    'valor': datos['valor'],
                    'descripcion': datos['descripcion']
                })
        else:
            form = IngresoForm()
      
    return render(request, 'ingreso/ingreso_form.html', {
        'form': form,
        'total_ingresos': total_ingresos,
    })