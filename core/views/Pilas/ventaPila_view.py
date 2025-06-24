from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from core.services.pilas_service import get_pilas_paginated, update_pila_stock_venta
from core.models.pilas import Pilas
from core.models.VentaPila import VentaPila
from datetime import datetime
from core.services.ingreso_service import crear_ingreso


@login_required
@require_http_methods(["GET"])
def ventaPilas_list_view(request):
    # Use the service to get paginated pilas
    page_number = request.GET.get('page')
    pilas = get_pilas_paginated(page_number)

    context = {
        'pilas': pilas,
    }
    return render(request, 'pilas/ventaPila_list.html', context)


@login_required
@require_http_methods(["POST"])
def ventaPila_view(request):
    """Procesar la venta de pilas"""
    if request.method == "POST":
        # Obtener los datos del request
        pilas_data = {}
        for key, value in request.POST.items():
            # Verificar que la clave comience con 'cantidad_' y el valor sea un número válido
            if key.startswith('cantidad_') and value.strip():
                try:
                    cantidad = int(value)
                    if cantidad > 0:  # Solo procesar cantidades positivas
                        pila_id = key.replace('cantidad_', '')
                        precio_key = f'precio_{pila_id}'
                        precio = request.POST.get(precio_key, '0').strip()
                        precio = int(
                            precio) if precio and precio.isdigit() else 0

                        pilas_data[pila_id] = {
                            'cantidad': cantidad,
                            'precio': precio
                        }
                except ValueError:
                    # Si el valor no es un entero válido, ignorarlo
                    continue

        if not pilas_data:
            messages.error(
                request, "No se han seleccionado pilas para la venta.")
            return redirect('ventaPila_list')

        # Procesar la venta
        try:
            # Variables para el registro de ingreso
            total_ingreso = 0
            descripcion_items = []

            # Procesar cada pila seleccionada
            for pila_id, datos in pilas_data.items():
                cantidad = datos['cantidad']
                precio_unitario = datos['precio']

                pila = Pilas.objects.get(id=pila_id)

                # Verificar stock suficiente
                if int(pila.cantidad) < cantidad:
                    messages.error(
                        request, f"Stock insuficiente para la pila {pila.codigo}.")
                    return redirect('ventaPila_list')

                # Calcular precio total para esta pila
                precio_total = precio_unitario * cantidad
                total_ingreso += precio_total

                # Registrar la venta
                venta = VentaPila(
                    pila=pila,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    fecha_venta=datetime.now()
                )
                venta.save()

                # Actualizar el stock
                update_pila_stock_venta(pila.id, cantidad)

                # Añadir a la descripción del ingreso
                descripcion_items.append(
                    f"{cantidad} pilas {pila.codigo} a ${precio_unitario} c/u")

            # Registrar el ingreso total de la venta
            if total_ingreso > 0:
                datos_ingreso = {
                    'fecha': datetime.now().strftime('%d/%m/%Y'),
                    'valor': str(total_ingreso),
                    'descripcion': "Venta de pilas: " + ", ".join(descripcion_items)
                }
                crear_ingreso(datos_ingreso)

            messages.success(request, "Venta agregada correctamente.")
            return redirect('ventaPila_list')

        except Exception as e:
            messages.error(request, f"Error al procesar la venta: {str(e)}")
            return redirect('ventaPila_list')

    return redirect('ventaPila_list')
