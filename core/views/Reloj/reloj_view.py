from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from core.forms.reloj_form import RelojForm
from core.services.reloj_service import get_all_relojes, create_reloj
from django.core.paginator import Paginator
from django.db.models import Q
from core.models.reloj import Reloj

@login_required
@require_http_methods(["GET", "POST"])
def reloj_list_view(request):
    filtro_estado = request.GET.get('estado', '')
    search_query = request.GET.get('search', '')

    relojes = get_all_relojes()

    if filtro_estado and filtro_estado != 'todos':
        relojes = relojes.filter(estado=filtro_estado)
    
    if search_query:
        search_terms = search_query.split()
        query = Q()
        base_query = (
            Q(referencia__icontains=search_query) 
        )
        query |= base_query

        relojes = relojes.filter(query).distinct()

    relojes = relojes.order_by('referencia')

    paginator = Paginator(relojes, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'relojes': page_obj,
        'page_obj': page_obj,
        'is_paginated': bool(relojes),
        'search': search_query,
        'filtro_estado': filtro_estado,
        'estados': [('todos', 'Todos')] + list(Reloj.ESTADO_CHOICES),
    }

    return render(request, 'reloj/reloj_list.html',context)

@login_required
@require_http_methods(["GET", "POST"])
def reloj_create_view(request):
    if request.method == 'POST':
        form = RelojForm(request.POST)
        print(form)
        if form.is_valid():
            create_reloj(form)
            messages.success(request, 'Referencia de reloj agregada con éxito')
            return redirect('reloj_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RelojForm()
    
    context = {'form': form, 'modo': 'crear'}
    return render(request, 'reloj/reloj_form.html', context)

@login_required
@require_http_methods(["GET", "POST"])
def reloj_update_view(request, pk):
    try:
        reloj = Reloj.objects.get(pk=pk)
    except Reloj.DoesNotExist:
        messages.error(request, 'El reloj no existe.')
        return redirect('reloj_list')
    
    if request.method == 'POST':
        form = RelojForm(request.POST, instance=reloj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Referencia de reloj actualizada con éxito')
            return redirect('reloj_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RelojForm(instance=reloj)
    
    context = {'form': form, 'modo': 'editar'}
    return render(request, 'reloj/reloj_form.html', context)

@login_required
@require_http_methods(["GET", "POST"])
def reloj_sell_view(request, pk):
    try:
        reloj = Reloj.objects.get(pk=pk)
    except Reloj.DoesNotExist:
        messages.error(request, 'El reloj no existe.')
        return redirect('reloj_list')
    
    if request.method == 'POST':
        form = RelojForm(request.POST, instance=reloj)
        if form.is_valid():
            reloj = form.save(commit=False)
            reloj.estado = 'vendido'
            reloj.save()
            messages.success(request, 'Referencia de reloj vendida con éxito')
            return redirect('reloj_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RelojForm(instance=reloj)
    
    context = {'form': form, 'modo': 'vender'}
    return render(request, 'reloj/reloj_form.html', context)