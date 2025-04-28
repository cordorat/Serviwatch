from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, get_user_model, login
from core.forms.login_form import LoginForm

def Login(request):
    if request.method == 'GET':
        return render(request, 'login/login.html', {
            'form': LoginForm()
        })
    else:
        usuario = request.POST.get('usuario', '')
        contraseña = request.POST.get('contraseña', '')
        
        if not usuario or not contraseña:
            form = LoginForm()
            return render(request, 'login/login.html', {
                'form': form,
                'error': "Ingrese las credenciales",
                'usuario_error': not usuario,
                'contraseña_error': not contraseña
            })

        try:
            user = get_user_model().objects.get(username=usuario)
        except get_user_model().DoesNotExist:
            form = LoginForm()
            return render(request, 'login/login.html', {
                'form': form,
                'error': "Usuario inexistente"
            })

        user = authenticate(request, username=usuario, password=contraseña)
        if user is None:
            form = LoginForm()
            return render(request, 'login/login.html', {
                'form': form,
                'error': "Usuario o contraseña incorrectos"
            })
        else:
            login(request, user)
            if user.is_superuser:
                return redirect('cliente_create')
            return redirect('cliente_list')