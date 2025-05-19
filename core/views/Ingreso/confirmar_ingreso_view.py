from core.services.ingreso_service import _procesar_confirmacion, _formatear_datos_ingreso
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def confirmar_ingreso_view(request):
    ingreso_data = request.session.get('ingreso_data')
    if not ingreso_data:
        return redirect('ingreso')  # Redirige si no hay datos en la sesión

    if request.method == 'POST':
        if 'confirmar' in request.POST:
            return _procesar_confirmacion(request, ingreso_data)
        elif 'editar' in request.POST:
            # Mantiene los datos en sesión y regresa al formulario
            return redirect('ingreso')

    # Para solicitudes GET, formatear datos para la plantilla
    ingreso_data_formateado = _formatear_datos_ingreso(ingreso_data)
    return render(request, 'ingreso/confirmar_ingreso.html', {'ingreso': ingreso_data_formateado})