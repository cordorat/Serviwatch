from core.services.egreso_service import _parsear_fecha, _crear_egreso_y_responder
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

formato_fecha = '%d/%m/%Y'

@login_required
def confirmar_egreso_view(request):
    egreso_data = request.session.get('egreso_data')
    if not egreso_data:
        return redirect('egreso')  # Redirige si no hay datos en la sesión

    if request.method == 'POST':
        if 'confirmar' in request.POST:
            # Preparar datos y crear egreso
            fecha = _parsear_fecha(egreso_data['fecha'])
            datos = {
                'fecha': fecha,
                'valor': egreso_data['valor'],
                'descripcion': egreso_data['descripcion']
            }
            return _crear_egreso_y_responder(request, datos)
            
        elif 'editar' in request.POST:
            # Mantiene los datos en sesión y regresa al formulario
            return redirect('egreso')

    # Para solicitudes GET, formatear fecha para mostrar en la plantilla
    fecha_obj = _parsear_fecha(egreso_data['fecha'])
    fecha_formateada = fecha_obj.strftime(formato_fecha)
    
    egreso_data_formateado = {
        'fecha': fecha_formateada,
        'valor': egreso_data['valor'],
        'descripcion': egreso_data['descripcion']
    }

    return render(request, 'egreso/confirmar_egreso.html', {'egreso': egreso_data_formateado})