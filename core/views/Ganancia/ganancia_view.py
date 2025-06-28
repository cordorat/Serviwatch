from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def ganancia_view(request):
    """
    Vista para mostrar la página de ganancia.
    """
    context = {
        # Aquí puedes agregar datos específicos para el template de ganancia
    }
    return render(request, 'ganancia/ganancia.html', context)
