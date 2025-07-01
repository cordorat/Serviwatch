from core.models.empleado import Empleado
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages

def crear_empleado(form):
    empleado = form.save()
    return empleado

def get_all_empleados(filtro_estado=None, busqueda_cedula=None):
    empleados = Empleado.objects.all()

    if filtro_estado:
        empleados = empleados.filter(estado=filtro_estado)

    if busqueda_cedula:
        empleados = empleados.filter(cedula__icontains=busqueda_cedula)

    return empleados.order_by('nombre')

def _initialize_empleado(id):
    """Inicializa el empleado y el modo según el ID."""
    if id:
        return get_object_or_404(Empleado, id=id), 'editar'
    return None, 'agregar'

def _handle_form_success(request, modo):
    """Maneja la respuesta exitosa después de guardar un empleado."""
    success_message = f'Empleado {"editado" if modo == "editar" else "creado"} exitosamente.'
    messages.success(request, success_message)
    
    # Para solicitudes AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': success_message})
    
    # Para solicitudes que requieren mostrar modal
    if request.headers.get('X-Show-Modal') == 'true':
        return JsonResponse({'success': True, 'redirect': f"{request.path}?success=true"})
    
    # Para solicitudes normales
    return redirect('empleado_list')

def _handle_form_error(request, error_message, form=None):
    """Maneja los errores de formulario o excepciones."""
    messages.error(request, f'Error: {error_message}')
    
    # Para solicitudes AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        response_data = {'success': False, 'message': error_message}
        
        # Si hay errores de formulario específicos
        if form and form.errors:
            response_data['errors'] = {field: error[0] for field, error in form.errors.items()}
        
        return JsonResponse(response_data, status=400)
    
    # Para solicitudes normales, el error ya se muestra con messages
    return None


### Generación de PDF de empleados ###

import io
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generar_pdf_empleados(empleados, filtro_estado):
    """
    Genera un reporte PDF de empleados basado en los filtros aplicados.
    
    Args:
        empleados: QuerySet de empleados filtrados
        filtro_estado: Estado seleccionado para el filtro
        request: Objeto de solicitud HTTP (opcional)
    
    Returns:
        bytes: Contenido del PDF generado
    """
    # Crear un buffer para el PDF
    buffer = io.BytesIO()
    
    # Configurar el documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Lista para almacenar los elementos del PDF
    elements = []
    
    # Estilos de texto
    styles = getSampleStyleSheet()
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        alignment=1,  # Centrado
        spaceAfter=10
    )
    normal_style = styles["Normal"]
    date_style = ParagraphStyle(
        'DateStyle',
        parent=normal_style,
        fontSize=10,
        alignment=1,  # Centrado
        spaceAfter=5
    )
    
    # Intentar agregar logo
    try:
        from django.contrib.staticfiles import finders
        logo_path = finders.find('images/logo.png')
        if logo_path:
            from reportlab.platypus import Image
            logo = Image(logo_path, width=2.5*inch, height=1*inch, hAlign='LEFT')
            elements.append(logo)
            elements.append(Spacer(1, 0.1*inch))
    except Exception:
        # Si hay algún error con el logo, simplemente continuamos sin él
        pass
    
    # Encabezado con datos de la empresa
    elements.append(Paragraph("Calle 25 Norte # 5 an -17", normal_style))
    elements.append(Paragraph("Tel: 555-1234", normal_style))
    elements.append(Spacer(1, 0.05*inch))
    
    # Título del reporte
    elements.append(Paragraph("REPORTE DE EMPLEADOS", subtitle_style))
    
    # Estado del filtro
    estado_texto = "TODOS"
    if filtro_estado and filtro_estado != 'todos':
        for estado_valor, estado_nombre in Empleado.ESTADO_CHOICES:
            if estado_valor == filtro_estado:
                estado_texto = estado_nombre
                break
    
    elements.append(Paragraph(f"Estado: {estado_texto}", date_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Preparar los datos para la tabla
    table_data = [
        ["Cédula", "Nombre", "Apellidos", "Teléfono", "Cargo"]  # Encabezados
    ]
    
    # Agregar cada empleado a la tabla
    for empleado in empleados:
        table_data.append([
            empleado.cedula,
            empleado.nombre,
            empleado.apellidos,
            empleado.celular,
            empleado.cargo,
        ])
    
    # Crear la tabla
    if table_data:
        table = Table(table_data, colWidths=[doc.width/6.0]*6)
        
        # Estilo de la tabla
        table_style = TableStyle([
            # Encabezados
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d4e484')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Datos
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Líneas
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ])
        
        # Aplicar el estilo a la tabla
        table.setStyle(table_style)
        elements.append(table)
    else:
        elements.append(Paragraph("No se encontraron empleados con los filtros aplicados.", normal_style))
    
    # Agregar pie de página
    elements.append(Spacer(1, 0.5*inch))
    
    # Información de generación del reporte
    footer_text = f"Generado el {timezone.now().strftime('%d/%m/%Y %H:%M')}"
    elements.append(Paragraph(footer_text, normal_style))
    
    # Construir el PDF
    doc.build(elements)
    
    # Obtener el contenido del PDF
    buffer.seek(0)
    return buffer.getvalue()