from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import IntegrityError
from core.forms.usuario_form import FormularioRegistroUsuario
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

@login_required
@require_http_methods(["GET"])
def usuario_list_view(request):
    usuarios = User.objects.all()
    return render(request, "usuario/usuario_list.html",{"usuarios":usuarios})

@login_required
@require_http_methods(["GET", "POST"])
def usuario_create_view(request):
    if request.method == 'POST':
        form = FormularioRegistroUsuario(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, 'Usuario creado exitosamente')
                return redirect('usuario_list')  
            except IntegrityError:
                form.add_error('username', 'El nombre de usuario ya existe')
                messages.error(request, 'Error al crear el usuario')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario')
            print(form.errors) 
    else:
        form = FormularioRegistroUsuario()
    
    return render(request, 'usuario/usuario_form.html', {
        'form': form
    })
