from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from core.forms.usuario_form import FormularioRegistroUsuario, FormularioEditarUsuario
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from core.services.usuario_service import crear_usuario, get_all_usuarios
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator

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
    if request.method == 'POST':
        form = FormularioRegistroUsuario(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                crear_usuario(
                    username=data['username'],
                    password=data['password1'],
                    email=data['email']
                )
                messages.success(request, 'SE AGREGÓ EL USUARIO CON ÉXITO')
                return redirect('usuario_list')  
            except ValidationError as e:
                form.add_error(None, e)
                messages.error(request, 'Error al crear el usuario')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario')
            print(form.errors) 
    else:
        form = FormularioRegistroUsuario()
    
    return render(request, 'usuario/usuario_form.html', {
        'form': form, 'modo': 'crear'
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
            messages.success(request, 'SE EDITÓ EL USUARIO CON ÉXITO')
            return redirect('usuario_list')
        else:
            messages.error(request, 'Error al actualizar el usuario')
    else:
        form = FormularioEditarUsuario(instance=usuario)

    return render(request, 'usuario/usuario_form.html', {
        'form': form,
        'modo': 'editar',
    })

@login_required
@require_http_methods(["GET", "POST"])
def usuario_delete_view(request, pk):
    try:
        usuario = User.objects.get(pk=pk)
    except User.DoesNotExist:
        messages.error(request, 'El usuario no existe.')
        return redirect('usuario_list')

    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'SE ELIMINÓ EL USUARIO CON ÉXITO')
        return redirect('usuario_list')

    return redirect('usuario_list')