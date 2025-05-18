from core.forms.ingreso_form import ReporteIngresoForm
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from core.services.ingreso_service import (
    obtener_ingresos_rango,
    obtener_total_ingresos_rango,
    generar_pdf_ingresos
)
from datetime import datetime
from django.shortcuts import render

@login_required
@require_http_methods(["GET"])
def reporte_ingresos_pdf(request):
    """
    Vista para generar un reporte PDF de ingresos en un rango de fechas.
    Parámetros GET:
        - inicio: Fecha de inicio en formato YYYY-MM-DD
        - fin: Fecha de fin en formato YYYY-MM-DD
    """
    fecha_inicio = request.GET.get('inicio')
    fecha_fin = request.GET.get('fin')

    # Validar que se proporcionaron las fechas
    if not fecha_inicio or not fecha_fin:
        return HttpResponse("Debes proporcionar el rango de fechas en los parámetros 'inicio' y 'fin'.", 
                           status=400)
    
    try:
        # Convertir fechas de string a objetos date
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        # Validar que la fecha de inicio no sea posterior a la fecha de fin
        if fecha_inicio > fecha_fin:
            return HttpResponse("La fecha de inicio no puede ser posterior a la fecha de fin.", 
                               status=400)
            
        # Obtener los ingresos y el total en el rango especificado
        ingresos = obtener_ingresos_rango(fecha_inicio, fecha_fin)
        total = obtener_total_ingresos_rango(fecha_inicio, fecha_fin)
        
        # Generar el PDF
        pdf = generar_pdf_ingresos(ingresos, fecha_inicio, fecha_fin, total, request)
        
        # Devolver el PDF como respuesta HTTP
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'filename="reporte_ingresos_{fecha_inicio}_{fecha_fin}.pdf"'
        return response
        
    except ValueError:
        return HttpResponse("Formato de fecha inválido. Usa el formato YYYY-MM-DD.", status=400)
    except Exception as e:
        return HttpResponse(f"Error al generar el reporte: {str(e)}", status=500)


@login_required
def reporte_ingresos_form(request):
    """
    Vista para mostrar el formulario de generación de reportes de ingresos
    """
    form = ReporteIngresoForm(request.GET or None)

    # Si hay datos GET, validar el formulario
    if request.GET:
        if form.is_valid():
            # El formulario es válido, el usuario será redirigido al PDF
            pass
        else:
            # El formulario no es válido, se mostrará con errores
            print("Errores del formulario:", form.errors)  # Para depuración
            
    return render(request, 'ingreso/ingreso_reporte_form.html', {'form': form})