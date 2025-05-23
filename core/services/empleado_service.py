from core.models.empleado import Empleado
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages

def crear_empleado(form):
    empleado = form.save()
    return empleado

def get_all_empleados(filtro_estado=None, busqueda_cedula=None):
    empleados = Empleado.objects.all()

    if filtro_estado:
        empleados = empleados.filter(estado=filtro_estado)

    if busqueda_cedula:
        empleados = empleados.filter(cedula__icontains=busqueda_cedula)

    return empleados.order_by('nombre')

def _initialize_empleado(id):
    """Inicializa el empleado y el modo según el ID."""
    if id:
        return get_object_or_404(Empleado, id=id), 'editar'
    return None, 'agregar'

def _handle_form_success(request, empleado, modo):
    """Maneja la respuesta exitosa después de guardar un empleado."""
    success_message = f'Empleado {"editado" if modo == "editar" else "creado"} exitosamente.'
    messages.success(request, success_message)
    
    # Para solicitudes AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': success_message})
    
    # Para solicitudes que requieren mostrar modal
    if request.headers.get('X-Show-Modal') == 'true':
        return JsonResponse({'success': True, 'redirect': f"{request.path}?success=true"})
    
    # Para solicitudes normales
    return redirect('empleado_list')

def _handle_form_error(request, error_message, form=None):
    """Maneja los errores de formulario o excepciones."""
    messages.error(request, f'Error: {error_message}')
    
    # Para solicitudes AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        response_data = {'success': False, 'message': error_message}
        
        # Si hay errores de formulario específicos
        if form and form.errors:
            response_data['errors'] = {field: error[0] for field, error in form.errors.items()}
        
        return JsonResponse(response_data, status=400)
    
    # Para solicitudes normales, el error ya se muestra con messages
    return None