from core.services import ingreso_service
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.http import JsonResponse

formato_fecha = '%d/%m/%Y'

@login_required
def confirmar_ingreso_view(request):
    ingreso_data = request.session.get('ingreso_data')
    if not ingreso_data:
        return redirect('ingreso')  # Redirige si no hay datos en la sesión

    if request.method == 'POST':
        if 'confirmar' in request.POST:
            # Preparar datos para el servicio
            try:
                fecha = datetime.strptime(ingreso_data['fecha'], '%Y-%m-%d').date()
            except ValueError:
                try:
                    fecha = datetime.strptime(ingreso_data['fecha'], formato_fecha).date()
                except ValueError:
                    fecha = datetime.strptime(ingreso_data['fecha'], '%d-%m-%Y').date()
            datos = {
                'fecha': fecha,
                'valor': ingreso_data['valor'],
                'descripcion': ingreso_data['descripcion']
            }
            
            # Guarda en la base de datos
            ingreso_service.crear_ingreso(datos)
            
            # Mensaje de éxito
            messages.success(request, "Ingreso registrado con éxito")
            
            # Limpia la sesión
            del request.session['ingreso_data']
            
            # Manejar solicitudes AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': "Ingreso registrado con éxito"
                })
            
            # Para solicitudes normales
            return redirect('ingreso')
        
        elif 'editar' in request.POST:
            # Mantiene los datos en sesión y regresa al formulario
            return redirect('ingreso')

    # Formatear fecha para mostrar en la plantilla
    try:
        # Intenta primero el formato previo
        fecha_obj = datetime.strptime(ingreso_data['fecha'], '%Y-%m-%d').date()
    except ValueError:
        try:
            # Intenta el formato con guiones
            fecha_obj = datetime.strptime(ingreso_data['fecha'], '%d-%m-%Y').date()
        except ValueError:
            # Intenta el formato con barras
            fecha_obj = datetime.strptime(ingreso_data['fecha'], formato_fecha).date()
    
    fecha_formateada = fecha_obj.strftime(formato_fecha)
    ingreso_data_formateado = {
        'fecha': fecha_formateada,
        'valor': ingreso_data['valor'],
        'descripcion': ingreso_data['descripcion']
    }

    return render(request, 'ingreso/confirmar_ingreso.html', {'ingreso': ingreso_data_formateado})