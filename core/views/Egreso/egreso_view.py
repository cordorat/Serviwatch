from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.forms.egreso_form import EgresoForm
from core.services.egreso_service import crear_egreso, obtener_datos_resumen
from django.shortcuts import render
from django.db.models import Sum
from datetime import date
from core.models import Egreso

def egreso_view(request):
    if request.method == 'POST':
        form = EgresoForm(request.POST)
        if form.is_valid():
            # Convertir fecha a string en formato ISO para almacenar en sesión
            fecha_str = form.cleaned_data['fecha'].isoformat()
            
            datos_egreso = {
                'fecha_str': fecha_str,  # Guardar como string
                'valor': int(form.cleaned_data['valor']),  # Convertir Decimal a float
                'descripcion': form.cleaned_data['descripcion']
            }
            # Guardar en sesión para confirmar
            request.session['datos_egreso'] = datos_egreso
            return redirect('confirmar_egreso')
    else:
        # Si hay datos en sesión, usarlos para editar
        if 'datos_egreso' in request.session:
            # Convertir de vuelta a fecha para el formulario
            datos = request.session['datos_egreso'].copy()
            
            # Convertir fecha_str a objeto date para el formulario
            from datetime import datetime
            datos['fecha'] = datetime.fromisoformat(datos.pop('fecha_str')).date()
            
            form = EgresoForm(initial=datos)
        else:
            form = EgresoForm()
    today = date.today()
    total_egresos = Egreso.objects.filter(fecha=today).aggregate(
        total=Sum('valor')
    )['total'] or 0

    return render(request, 'egreso/egreso_form.html', {
        'form': form,
        'total_egresos': total_egresos
    })
    


def confirmar_egreso_view(request):
    if 'datos_egreso' not in request.session:
        return redirect('egreso')
    
    datos = request.session['datos_egreso']
    
    if request.method == 'POST':
        if 'confirmar' in request.POST:
            # Convertir fecha_str de vuelta a objeto date para guardar
            from datetime import datetime
            datos_para_guardar = datos.copy()
            datos_para_guardar['fecha'] = datetime.fromisoformat(datos['fecha_str']).date()
            
            # Guardar en base de datos
            crear_egreso(datos_para_guardar)
            messages.success(request, "Egreso ingresado con éxito")
            # Limpiar sesión
            success_message = 'EGRESO AGREGADO CORRECTAMENTE'
            del request.session['datos_egreso']
            return render(request, 'egreso/confirmar_egreso.html', {
                    'success': success_message})
        elif 'editar' in request.POST:
            # Volver al formulario para editar
            return redirect('egreso')
    
    # Preparar datos para mostrar en confirmación
    from datetime import datetime
    datos_para_resumen = datos.copy()
    datos_para_resumen['fecha'] = datetime.fromisoformat(datos['fecha_str']).date()
    
    # Obtener datos formateados para mostrar en la confirmación
    resumen = obtener_datos_resumen(datos_para_resumen)
    return render(request, 'egreso/confirmar_egreso.html', {'resumen': resumen})
