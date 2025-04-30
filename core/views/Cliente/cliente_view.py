from django.shortcuts import render, redirect
from core.forms.cliente_form import ClienteForm
from core.services.cliente_service import get_all_clientes, crear_cliente
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

@login_required
@require_http_methods(["GET"])
def cliente_list_view(request):
    clientes = get_all_clientes()
    return render(request, "cliente/cliente_list.html", {"clientes": clientes})


@login_required
@require_http_methods(["GET", "POST"])
def cliente_create_view(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            crear_cliente(form)
            return redirect('cliente_list')
    else:
        form = ClienteForm()

    return render(request, 'cliente/cliente_form.html', {'form': form})
