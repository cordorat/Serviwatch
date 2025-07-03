from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from core.forms.reloj_form import RelojForm
from core.services.reloj_service import get_all_relojes, create_reloj, generar_pdf_relojes
from django.core.paginator import Paginator
from django.db.models import Q
from core.models.reloj import Reloj
from core.models.cliente import Cliente
from datetime import datetime
from django.http import HttpResponse

mensaje_de_error = 'Por favor corrige los errores en el formulario.'
templade_a_dirigir = 'reloj/reloj_form.html'

mensaje_de_error = 'Por favor corrige los errores en el formulario.'
templade_a_dirigir = 'reloj/reloj_form.html'

@login_required
@require_http_methods(["GET", "POST"])
def reloj_list_view(request):
    filtro_estado = request.GET.get('estado', '')
    filtro_tipo = request.GET.get('tipo', '')
    filtro_pagado = request.GET.get('pagado', '')
    search_query = request.GET.get('search', '')

    relojes = get_all_relojes()

    # Verificar si estamos en la URL de servicios
    filter_params = {}
    if 'servicios' in request.path:
        relojes = relojes.filter(pagado=False)
    elif filtro_estado and filtro_estado != 'todos':
        relojes = relojes.filter(estado=filtro_estado)
        filter_params['estado'] = filtro_estado

    if filtro_tipo and filtro_tipo != 'todos':
        relojes = relojes.filter(tipo=filtro_tipo)
        filter_params['tipo'] = filtro_tipo

    if filtro_pagado and filtro_pagado != 'todos':
        relojes = relojes.filter(pagado=filtro_pagado)
        filter_params['pagado'] = filtro_pagado

    if search_query:
        search_query.split()
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
        'filtro_tipo': filtro_tipo,
        'filtro_pagado': filtro_pagado,
        'filter_params': filter_params, 
        'pagado_options': [('todos', 'Todos'), ('True', 'Pagado'), ('False', 'No Pagado')],
        'estados': [('todos', 'Todos')] + list(Reloj.ESTADO_CHOICES),
        'tipos': [('todos', 'Todos')] + list(Reloj.TIPO_CHOICES),
        'is_servicios': 'servicios' in request.path 
    }

    return render(request, 'reloj/reloj_list.html', context)
    

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
            messages.error(request, mensaje_de_error)
    else:
        form = RelojForm()
    
    context = {'form': form, 'modo': 'crear'}
    return render(request, templade_a_dirigir, context)

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
            messages.error(request, mensaje_de_error)
    else:
        form = RelojForm(instance=reloj)
    
    context = {'form': form, 'modo': 'editar', 'reloj': reloj}
    return render(request, templade_a_dirigir, context)

@login_required
@require_http_methods(["GET", "POST"])
def reloj_sell_view(request, pk):
    try:
        reloj = Reloj.objects.get(pk=pk)
    except Reloj.DoesNotExist:
        messages.error(request, 'El reloj no existe.')
        return redirect('reloj_venta_list')
    
    if request.method == 'POST':
        form = RelojForm(request.POST, instance=reloj)
        
        # Obtener el monto del abono inicial
        abono_inicial_monto = request.POST.get('abono_inicial_monto')
        abono_inicial_desc = request.POST.get('abono_inicial_descripcion', 'Abono inicial')
        
        if form.is_valid():
            # Guardar la venta del reloj
            reloj = form.save(commit=False)
            reloj.estado = 'VENDIDO'
            reloj.fecha_venta = form.cleaned_data.get('fecha_venta')
            
            # Establecer el saldo pendiente según el método de pago y el abono
            if reloj.metodo_pago == 'CONTADO':
                reloj.saldo_pendiente = '0'
                reloj.pagado = True
            elif reloj.metodo_pago == 'ABONO':
                # Si hay abono inicial, aplicarlo
                if abono_inicial_monto and int(abono_inicial_monto) > 0:
                    precio = int(reloj.saldo_pendiente)  # Usar saldo_pendiente en lugar del precio
                    abono = int(abono_inicial_monto)
                    nuevo_saldo = max(0, precio - abono)
                    
                    # Asignar el nuevo saldo pendiente
                    reloj.saldo_pendiente = str(nuevo_saldo)
                    reloj.pagado = (nuevo_saldo == 0)
                    
                    print(f"DEBUG - Precio: {precio}, Abono: {abono}, Nuevo saldo: {nuevo_saldo}")
                else:
                    # Si no hay abono, el saldo es el precio total
                    reloj.saldo_pendiente = reloj.precio
                    reloj.pagado = False
            
            # Guardar el reloj con los cambios
            reloj.save()
            
            # Si hay abono, registrarlo
            if abono_inicial_monto and int(abono_inicial_monto) > 0:
                from core.models.abono import Abono
                from django.utils import timezone
                
                # Crear el registro de abono
                abono = Abono.objects.create(
                    reloj=reloj,
                    monto=abono_inicial_monto,
                    descripcion=abono_inicial_desc,
                    fecha=timezone.now()
                )
                
                # Registrar el ingreso
                from core.services.ingreso_service import crear_ingreso
                datos_ingreso = {
                    'fecha': timezone.now().strftime('%d/%m/%Y'),
                    'valor': abono_inicial_monto,
                    'descripcion': f"Abono inicial reloj {reloj.referencia} - {reloj.marca}"
                }
                crear_ingreso(datos_ingreso)
                
                messages.success(
                    request, 
                    f'Reloj vendido con abono de ${abono_inicial_monto}. Saldo pendiente: ${reloj.saldo_pendiente}'
                )
            else:
                messages.success(request, 'Reloj vendido exitosamente.')
            
            # Guardar de nuevo para asegurar que todos los cambios se aplican
            reloj.save()
            
            # Verificar que el saldo pendiente se actualizó correctamente
            reloj_actualizado = Reloj.objects.get(pk=reloj.pk)
            print(f"DEBUG - Saldo pendiente final en BD: {reloj_actualizado.saldo_pendiente}")
            
            return redirect('reloj_venta_list')
    else:
        form = RelojForm(instance=reloj)
    
    context = {
        'form': form,
        'modo': 'vender',
        'reloj': reloj,
        'clientes': Cliente.objects.all().order_by('nombre')
    }
    return render(request, 'reloj/reloj_form.html', context)

@require_http_methods(["GET"])
def reporte_relojes_pdf(request):
    """
    Vista para generar un reporte PDF de relojes con los mismos filtros
    que se están usando en la vista de lista.
    """
    filtro_estado = request.GET.get('estado', '')
    filtro_tipo = request.GET.get('tipo', '')
    filtro_pagado = request.GET.get('pagado', '')
    search_query = request.GET.get('search', '')

    # Usar la misma lógica de filtrado que en reloj_list_view
    relojes_qs = get_all_relojes()

    # Verificar si estamos en la URL de servicios (relojes no pagados)
    if 'servicios' in request.META.get('HTTP_REFERER', ''):
        relojes_qs = relojes_qs.filter(pagado=False)
    elif filtro_estado and filtro_estado != 'todos':
        relojes_qs = relojes_qs.filter(estado=filtro_estado)

    if filtro_tipo and filtro_tipo != 'todos':
        relojes_qs = relojes_qs.filter(tipo=filtro_tipo)

    if filtro_pagado and filtro_pagado != 'todos':
        relojes_qs = relojes_qs.filter(pagado=filtro_pagado)

    if search_query:
        query = Q()
        base_query = (
            Q(referencia__icontains=search_query) 
        )
        query |= base_query
        relojes_qs = relojes_qs.filter(query).distinct()

    relojes_qs = relojes_qs.order_by('referencia')
    
    try:
        # Generar el PDF
        pdf = generar_pdf_relojes(relojes_qs, filtro_estado, filtro_tipo, request)
        
        # Devolver el PDF como respuesta HTTP
        estado_texto = filtro_estado if filtro_estado and filtro_estado != 'todos' else 'todos'
        tipo_texto = filtro_tipo if filtro_tipo and filtro_tipo != 'todos' else 'todos'
        filename = f"reporte_relojes_{estado_texto}_{tipo_texto}.pdf"
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'filename="{filename}"'
        return response
        
    except Exception as e:
        return HttpResponse(f"Error al generar el reporte: {str(e)}", status=500)
