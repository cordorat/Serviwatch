from datetime import date
from django.shortcuts import render, redirect
from core.services.ingreso_service import obtener_total_ingresos_dia 
from core.forms.ingreso_form import IngresoForm
from django.contrib.auth.decorators import login_required


@login_required
def ingreso_view(request):
    total_ingresos = obtener_total_ingresos_dia()

    if request.method == 'POST':
        form = IngresoForm(request.POST)
        if form.is_valid():
            # Crea el objeto pero NO lo guarda
            form.save(commit=False)
            # Pasa el objeto a la vista de confirmación
            request.session['ingreso_data'] = {
                'fecha': str(form.cleaned_data['fecha']),
                'valor': form.cleaned_data['valor'],
                'descripcion': form.cleaned_data['descripcion']
            }
            return redirect('confirmar_ingreso')
    else:
        # Si hay datos en sesión (viniendo de "editar"), usarlos para el formulario
        if 'ingreso_data' in request.session:
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