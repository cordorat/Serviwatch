from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import IntegrityError
from core.forms.usuario_form import FormularioRegistroUsuario

def usuario_list_view(request):
    return render(request, "usuario/usuario_list.html")


def usuario_create_view(request):
    if request.method == 'GET':
        return render(request, 'usuario/usuario_form.html', {
            'form': FormularioRegistroUsuario()
        })
    else:
        form = FormularioRegistroUsuario(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                return redirect('usuario_create')
            except IntegrityError:
                form.add_error('username', 'El nombre de usuario ya existe')
    return render(request, 'usuario/usuario_form.html', {
        'form': form
    })
