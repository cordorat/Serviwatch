from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from core.models.reloj import Reloj
from core.forms.abono_form import AbonoForm
from core.services.abono_service import registrar_abono

@login_required
@require_http_methods(["POST"])
def abono_create_view(request, reloj_id): 
    reloj = get_object_or_404(Reloj, id=reloj_id)
    
    try:
        monto = request.POST.get('monto')
        descripcion = request.POST.get('descripcion', '')
        next_url = request.POST.get('next')
        
        if not monto:
            raise ValueError("El monto es requerido")
        
        abono, reloj_actualizado = registrar_abono(
            reloj_id=reloj_id,
            monto=monto,
            descripcion=descripcion
        )
        
        messages.success(
            request, 
            f'Abono por ${monto} registrado exitosamente. Saldo pendiente: ${reloj_actualizado.saldo_pendiente}'
        )
        
        if next_url:
            return redirect(next_url)
            
    except ValueError as e:
        messages.error(request, str(e))
        print(f"Error de validación: {str(e)}")
    except Exception as e:
        messages.error(request, "Error al procesar el abono")
        print(f"Error inesperado: {str(e)}")
    
    return redirect('reloj_edit', pk=reloj_id)