from django.shortcuts import render, redirect
from core.forms.cliente_form import ClienteForm
from core.services.cliente_service import get_all_clientes, crear_cliente
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q
from core.models.cliente import Cliente




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
            messages.success(request, 'Cliente creado exitosamente.')
            form.save()
            next_url = request.GET.get('next')
            if next_url (next_url):
                return redirect(next_url)

            return redirect('cliente_list')
    else:
        form = ClienteForm()
    return render(request, 'cliente/cliente_form.html', {'form': form})


def cliente_search_view(request):
    """Vista para búsqueda de clientes vía AJAX"""
    search_term = request.GET.get('term', '')
    print(f"Término de búsqueda recibido: {search_term}")  # Debug

    # Validar término de búsqueda
    if len(search_term) < 2:
        return JsonResponse([], safe=False)

    # Buscar clientes que coincidan
    clientes = Cliente.objects.filter(
        Q(nombre__icontains=search_term) | 
        Q(apellido__icontains=search_term) |
        Q(telefono__icontains=search_term)
    )[:10]
    

    # Formatear resultados
    results = []
    for cliente in clientes:
        results.append({
            'id': cliente.id,
            'label': f"{cliente.nombre} {cliente.apellido} - {cliente.telefono}",
            'value': f"{cliente.nombre} {cliente.apellido}",
            'telefono': cliente.telefono
        })

    print(f"Resultados encontrados: {results}")  # Debug
    return JsonResponse(results, safe=False)
