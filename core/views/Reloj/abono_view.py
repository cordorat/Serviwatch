from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from core.models.reloj import Reloj
from core.forms.abono_form import AbonoForm
from core.services.abono_service import registrar_abono, get_all_abonos

@login_required
@require_http_methods(["POST"])
def abono_create_view(request, reloj_id):
    reloj = get_object_or_404(Reloj, id=reloj_id)
    
    if request.method == 'POST':
        form = AbonoForm(request.POST)
        if form.is_valid():
            try:
                monto = form.cleaned_data['monto']
                descripcion = form.cleaned_data.get('descripcion', '')
                
                abono, reloj_actualizado = registrar_abono(reloj_id, monto, descripcion)
                messages.success(request, f'Abono por ${monto} registrado exitosamente. Saldo pendiente: ${reloj_actualizado.saldo_pendiente}')
                
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, "Error al procesar el abono")
                print(f"Error inesperado: {str(e)}")
        else:
            messages.error(request, "Por favor verifique los datos del abono")
    
    return redirect('reloj_form', pk=reloj_id)