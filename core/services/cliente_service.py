from core.models import Cliente
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.contrib import messages

def get_all_clientes():
    return Cliente.objects.all()

def crear_cliente(form):
    return form.save()

def _initialize_cliente(id):
    """Inicializa el cliente y el modo según el ID."""
    if id:
        return get_object_or_404(Cliente, id=id), 'editar'
    return None, 'agregar'


def _handle_ajax_response(form=None, modo='agregar', success=True):
    if success:
        message = 'Cliente editado exitosamente.' if modo == 'editar' else 'Cliente creado exitosamente.'
        return JsonResponse({
            'success': True,
            'message': message
        })
    else:
        # Devolver errores de validación en formato adecuado
        errors = {}
        if form:
            for field, error_list in form.errors.items():
                errors[field] = [str(error) for error in error_list]
                
        return JsonResponse({
            'success': False,
            'errors': errors,
            'message': 'Por favor, corrija los errores en el formulario.'
        }, status=400)


def _add_success_message(request, modo):
    """Agrega el mensaje de éxito apropiado."""
    message = 'Cliente editado exitosamente.' if modo == 'editar' else 'Cliente creado exitosamente.'
    messages.success(request, message)


def _render_cliente_form(request, form, modo):
    """Renderiza el formulario de cliente con el contexto adecuado."""
    return render(request, 'cliente/cliente_form.html', {
        'form': form,
        'modo': modo,
        'next_url': request.GET.get('next', reverse('cliente_list')),
    })