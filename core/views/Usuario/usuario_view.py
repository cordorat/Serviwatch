from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from core.forms.usuario_form import FormularioRegistroUsuario, FormularioEditarUsuario
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from core.services.usuario_service import crear_usuario, get_all_usuarios
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.shortcuts import get_object_or_404

@login_required
@require_http_methods(["GET"])
def usuario_list_view(request):
    usuarios = get_all_usuarios()
    
    usuarios = usuarios.order_by('username')

    paginator = Paginator(usuarios, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'usuarios': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }

    return render(request, "usuario/usuario_list.html",context)

@login_required
@require_http_methods(["GET", "POST"])
def usuario_create_view(request):
    # Verificar primero si es una solicitud de éxito
    success = request.GET.get('success') == 'true'
    
    # Si es success=true, mostrar un formulario completamente nuevo sin validación
    if success:
        form = FormularioRegistroUsuario()  # Formulario vacío sin validación
        return render(request, 'usuario/usuario_form.html', {
            'form': form,
            'modo': 'crear',
            'success': True
        })
    
    # Flujo normal para POST y GET sin success
    if request.method == 'POST':
        form = FormularioRegistroUsuario(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                usuario = crear_usuario(
                    username=data['username'],
                    password=data['password1'],
                    email=data['email']
                )
                
                # Si es una solicitud AJAX, devolver respuesta JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Usuario agregado correctamente'
                    })
                
                messages.success(request, 'SE AGREGÓ EL USUARIO CON ÉXITO')
                return redirect('usuario_list')
            except ValidationError as e:
                form.add_error(None, str(e))
                
                # Si es una solicitud AJAX, devolver errores en JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    errors = {field: error[0] for field, error in form.errors.items()}
                    return JsonResponse({
                        'success': False,
                        'errors': errors
                    }, status=400)
                    
                messages.error(request, 'Error al crear el usuario')
        else:
            # Si es una solicitud AJAX, devolver errores en JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = {field: error[0] for field, error in form.errors.items()}
                return JsonResponse({
                    'success': False,
                    'errors': errors
                }, status=400)
                
            messages.error(request, 'Por favor corrija los errores en el formulario')
    else:
        form = FormularioRegistroUsuario()
    
    return render(request, 'usuario/usuario_form.html', {
        'form': form,
        'modo': 'crear',
        'success': False
    })

@login_required
@require_http_methods(["GET", "POST"])
def usuario_update_view(request, pk):
    try:
        usuario = User.objects.get(pk=pk)
    except User.DoesNotExist:
        messages.error(request, 'El usuario no existe.')
        return redirect('usuario_list')
    
    if request.method == 'POST':
        form = FormularioEditarUsuario(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            
            # Si es una solicitud AJAX, devolver respuesta JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Usuario actualizado correctamente'
                })
                
            messages.success(request, 'SE EDITÓ EL USUARIO CON ÉXITO')
            return redirect('usuario_list')
        else:
            # Si es una solicitud AJAX, devolver errores en JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = {field: error[0] for field, error in form.errors.items()}
                return JsonResponse({
                    'success': False,
                    'errors': errors
                }, status=400)
                
            messages.error(request, 'Error al actualizar el usuario')
    else:
        form = FormularioEditarUsuario(instance=usuario)

    # Verificar si hay parámetro de éxito
    success = request.GET.get('success') == 'true'
    
    return render(request, 'usuario/usuario_form.html', {
        'form': form,
        'modo': 'editar',
        'success': success
    })

@login_required
@require_http_methods(["GET", "POST"])
def usuario_delete_view(request, pk):
    try:
        usuario = User.objects.get(pk=pk)
    except User.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'El usuario no existe.'}, status=404)
        messages.error(request, 'El usuario no existe.')
        return redirect('usuario_list')

    if request.method == 'POST':
        # Guardar el nombre de usuario para el mensaje
        username = usuario.username
        
        # Eliminar el usuario
        usuario.delete()
        
        # Responder apropiadamente según el tipo de solicitud
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': f'El usuario {username} ha sido eliminado exitosamente.'
            })
        
        messages.success(request, 'SE ELIMINÓ EL USUARIO CON ÉXITO')
        return redirect('usuario_list')

    # Si es GET y se solicita por AJAX, devolver un formulario
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
    return redirect('usuario_list')