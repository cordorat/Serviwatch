from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def usuario_contabilidad_view(request):
    return render(request, 'usuario_contabilidad.html')