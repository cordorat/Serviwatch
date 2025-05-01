from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from core.forms.usuario_form import FormularioRegistroUsuario
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from core.services.usuario_service import crear_usuario, get_all_usuarios
from django.core.exceptions import ValidationError

@login_required
@require_http_methods(["GET"])
def usuario_list_view(request):
    usuarios = get_all_usuarios()
    return render(request, "usuario/usuario_list.html",{"usuarios":usuarios})

@login_required
@require_http_methods(["GET", "POST"])
def usuario_create_view(request):
    if request.method == 'POST':
        form = FormularioRegistroUsuario(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                user = crear_usuario(
                    username=data['username'],
                    password=data['password1'],
                    email=data['email']
                )
                messages.success(request, 'Usuario creado exitosamente')
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
        'form': form
    })