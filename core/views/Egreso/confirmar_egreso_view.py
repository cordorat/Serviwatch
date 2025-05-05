from core.services import egreso_service
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime

@login_required
def confirmar_egreso_view(request):
    egreso_data = request.session.get('egreso_data')
    if not egreso_data:
        return redirect('egreso')  # Redirige si no hay datos en la sesión

    if request.method == 'POST':
        if 'confirmar' in request.POST:
            # Preparar datos para el servicio
            datos = {
                'fecha': datetime.strptime(egreso_data['fecha'], '%Y-%m-%d').date(),
                'valor': egreso_data['valor'],
                'descripcion': egreso_data['descripcion']
            }
            
            # Guarda en la base de datos
            egreso_service.crear_egreso(datos)
            
            # Mensaje de éxito
            messages.success(request, "Egreso ingresado con éxito")
            
            # Limpia la sesión
            del request.session['egreso_data']
            
            return redirect('egreso')
        
        elif 'editar' in request.POST:
            # Mantiene los datos en sesión y regresa al formulario
            return redirect('egreso')

    # Formatear fecha para mostrar en la plantilla
    fecha_formateada = datetime.strptime(egreso_data['fecha'], '%Y-%m-%d').date().strftime('%d/%m/%Y')
    egreso_data_formateado = {
        'fecha': fecha_formateada,
        'valor': egreso_data['valor'],
        'descripcion': egreso_data['descripcion']
    }

    return render(request, 'egreso/confirmar_egreso.html', {'egreso': egreso_data_formateado})