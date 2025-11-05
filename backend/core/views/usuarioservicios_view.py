from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def usuario_servicios_view(request):
    return render(request, 'usuario-servicios.html')