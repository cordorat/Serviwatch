from datetime import date
from django.shortcuts import render, redirect
from core.services.egreso_service import obtener_total_egresos_dia 
from core.forms.egreso_form import EgresoForm
from django.contrib.auth.decorators import login_required


@login_required
def egreso_view(request):
    total_egresos = obtener_total_egresos_dia()

    # Verificar si se debe limpiar la sesión (cuando se cancela)
    if request.GET.get('clear') == 'true':
        if 'egreso_data' in request.session:
            del request.session['egreso_data']
        if 'egreso_from_form' in request.session:
            del request.session['egreso_from_form']
        return redirect('egreso')  # Redirigir sin parámetros para limpiar la URL

    if request.method == 'POST':
        form = EgresoForm(request.POST)
        if form.is_valid():
            # Solo pasar los datos limpios a la sesión, sin crear objeto
            request.session['egreso_data'] = {
                'fecha': str(form.cleaned_data['fecha']),
                'valor': form.cleaned_data['valor'],
                'descripcion': form.cleaned_data['descripcion']
            }
            # Marcar que venimos del formulario para no limpiar en próxima visita
            request.session['egreso_from_form'] = True
            return redirect('confirmar_egreso')
        # Si el formulario NO es válido, se renderizará de nuevo con errores
    else:
        # Si hay datos en sesión, verificar si venimos de la confirmación o de navegación externa
        if 'egreso_data' in request.session:
            # Si no venimos del formulario/confirmación, limpiar automáticamente
            if not request.session.get('egreso_from_form', False):
                del request.session['egreso_data']
                if 'egreso_from_form' in request.session:
                    del request.session['egreso_from_form']
                form = EgresoForm()
            else:
                # Venimos de "editar", mantener los datos y resetear la bandera
                request.session['egreso_from_form'] = False
                from datetime import datetime
                datos = request.session['egreso_data']
                
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
                form = EgresoForm(initial={
                    'fecha': fecha,
                    'valor': datos['valor'],
                    'descripcion': datos['descripcion']
                })
        else:
            form = EgresoForm()
    return render(request, 'egreso/egreso_form.html', {
        'form': form,
        'total_egresos': total_egresos,
})