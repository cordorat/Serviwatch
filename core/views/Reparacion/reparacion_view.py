from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.forms.reparacion_form import ReparacionForm
from core.models.reparacion import Reparacion

@login_required
def reparacion_list_view(request):
    reparaciones = Reparacion.objects.all().order_by('estado')
    return render(request, 'reparacion/reparacion_list.html', {'reparaciones': reparaciones})

@login_required
def reparacion_create_view(request):
    if request.method == 'POST':
        form = ReparacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Reparación agregada correctamente.")
            return redirect('listar_reparaciones')
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = ReparacionForm()

    return render(request, 'core/reparaciones/agregar_reparacion.html', {'form': form})
