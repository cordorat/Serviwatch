from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from core.forms.reloj_form import RelojForm
from core.services.reloj_service import get_all_relojes, create_reloj
from django.core.paginator import Paginator

@login_required
@require_http_methods(["GET", "POST"])
def reloj_list_view(request):
    relojes = get_all_relojes()

    relojes = relojes.order_by('marca')

    paginator = Paginator(relojes, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'relojes': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }

    return render(request, 'reloj/reloj_list.html',context)

@login_required
@require_http_methods(["GET", "POST"])
def reloj_create_view(request):
    if request.method == 'POST':
        form = RelojForm(request.POST)
        if form.is_valid():
            create_reloj(form)
            messages.success(request, 'Referencia de reloj agregada con éxito')
            return redirect('reloj_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RelojForm()
    
    context = {'form': form}
    return render(request, 'reloj/reloj_form.html', context)