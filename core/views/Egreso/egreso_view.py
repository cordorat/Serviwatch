from datetime import date
from django.shortcuts import render, redirect
from core.services.egreso_service import obtener_total_egresos_dia 
from core.forms.egreso_form import EgresoForm
from django.contrib.auth.decorators import login_required


@login_required
def egreso_view(request):
    total_egresos = obtener_total_egresos_dia()

    if request.method == 'POST':
        form = EgresoForm(request.POST)
        if form.is_valid():
            # Crea el objeto pero NO lo guarda
            egreso = form.save(commit=False)
            # Pasa el objeto a la vista de confirmación
            request.session['egreso_data'] = {
                'fecha': str(form.cleaned_data['fecha']),
                'valor': form.cleaned_data['valor'],
                'descripcion': form.cleaned_data['descripcion']
            }
            return redirect('confirmar_egreso')
    else:
        # Si hay datos en sesión (viniendo de "editar"), usarlos para el formulario
        if 'egreso_data' in request.session:
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

