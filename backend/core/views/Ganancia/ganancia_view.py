from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from core.forms.ganancia_form import ReporteGananciaForm
from core.services.ganancia_service import (
    obtener_ganancia_hoy,
    calcular_ganancia_rango,
    generar_pdf_ganancias
)
from datetime import datetime


@login_required
def ganancia_view(request):
    """
    Vista para mostrar la página de ganancia con el formulario de reportes.
    """
    form = ReporteGananciaForm(request.GET or None)
    
    # Obtener la ganancia del día actual para mostrar en la página
    try:
        ganancia_hoy = obtener_ganancia_hoy()
    except Exception:
        ganancia_hoy = {
            'ganancia_neta': 0,
            'total_ingresos': 0,
            'total_egresos': 0
        }
    
    context = {
        'form': form,
        'total_ingresos': ganancia_hoy['ganancia_neta'],  # Mostrar ganancia neta en lugar de solo ingresos
        'ganancia_data': ganancia_hoy
    }
    
    # Si hay datos GET, validar el formulario
    if request.GET:
        if form.is_valid():
            # El formulario es válido, el usuario será redirigido al PDF
            pass
        else:
            # El formulario no es válido, se mostrará con errores
            print("Errores del formulario:", form.errors)  # Para depuración
    
    return render(request, 'ganancia/ganancia.html', context)


@login_required
@require_http_methods(["GET"])
def reporte_ganancias_pdf(request):
    """
    Vista para generar un reporte PDF de ganancias en un rango de fechas.
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
            
        # Calcular las ganancias en el rango especificado
        datos_ganancia = calcular_ganancia_rango(fecha_inicio, fecha_fin)
        
        # Generar el PDF
        pdf = generar_pdf_ganancias(fecha_inicio, fecha_fin, datos_ganancia, request)
        
        # Devolver el PDF como respuesta HTTP
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'filename="reporte_ganancias_{fecha_inicio}_{fecha_fin}.pdf"'
        return response
        
    except ValueError:
        return HttpResponse("Formato de fecha inválido. Usa el formato YYYY-MM-DD.", status=400)
    except Exception as e:
        return HttpResponse(f"Error al generar el reporte: {str(e)}", status=500)
