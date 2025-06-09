from core.models import Reparacion
from django.shortcuts import get_object_or_404

from io import BytesIO
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def get_all_reparaciones():
    return Reparacion.objects.all()

def crear_reparacion(form):
    return form.save()


def get_reparacion_by_id(id):
    """
    Obtiene una reparación por su ID.
    
    Args:
        id: ID de la reparación
        
    Returns:
        Reparacion: La reparación encontrada o None
    """
    try:
        return Reparacion.objects.get(pk=id)
    except Reparacion.DoesNotExist:
        return None

def actualizar_reparacion(form, reparacion_id):
    """
    Actualiza una reparación existente con los datos del formulario.
    
    Args:
        form: Formulario de reparación validado
        reparacion_id: ID de la reparación a actualizar
        
    Returns:
        Reparacion: La instancia de reparación actualizada
        
    Raises:
        ValueError: Si la reparación no existe
    """
    get_object_or_404(Reparacion, pk=reparacion_id)
    return form.save()


def generar_pdf_reparaciones(reparaciones, filtro_estado, request=None):
    """
    Genera un PDF con el listado de reparaciones filtradas.
    
    Args:
        reparaciones: QuerySet de reparaciones
        filtro_estado: Estado usado para filtrar (o 'todos')
        request: Objeto request para acceder a información del usuario
    
    Returns:
        BytesIO con el contenido del PDF
    """
    # Configurar el buffer y el documento
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        #pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
        title=f"Reporte de Reparaciones - {filtro_estado if filtro_estado != 'todos' else 'Todos los estados'}"
    )
    
    # Lista para almacenar todos los elementos del PDF
    elements = []
    
    # Configurar estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        alignment=1,  # Centrado
        spaceAfter=5,
        textColor=colors.black
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Heading2'],
        alignment=1,  # Centrado
        spaceAfter=2,
        textColor=colors.black
    )
    normal_style = styles['Normal']
    date_style = ParagraphStyle(
        'DateStyle',
        parent=normal_style,
        alignment=1,  # Centrado
        fontStyle='italic',
        textColor=colors.gray
    )

       # Estilo para texto en celdas
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=normal_style,
        fontSize=8,
        leading=10,  # Espacio entre líneas
        spaceBefore=2,
        spaceAfter=2
    )

    # Intentar incluir el logo si está disponible
    try:
        from django.contrib.staticfiles import finders
        logo_path = finders.find('images/logo.png')
        if logo_path:
            from reportlab.platypus import Image
            logo = Image(logo_path, width=2.5*inch, height=1*inch, hAlign='LEFT')
            elements.append(logo)
            elements.append(Spacer(1, 0.1*inch))
    except Exception as e:
        # Si hay algún error con el logo, simplemente continuamos sin él
        pass
    
    # Encabezado con datos de la empresa
    #elements.append(Paragraph("ServiWatch", title_style))
    elements.append(Paragraph("Calle 25 Norte # 5 an -17", normal_style))
    elements.append(Paragraph("Tel: 555-1234", normal_style))
    elements.append(Spacer(1, 0.05*inch))
    

    # Título del reporte
    titulo = "REPORTE DE REPARACIONES"
    if filtro_estado and filtro_estado != 'todos':
        titulo += f" - ESTADO: {filtro_estado.upper()}"
    elements.append(Paragraph(titulo, subtitle_style))
    
    elements.append(Spacer(1, 0.25*inch))
    
    # Preparar los datos para la tabla
    table_data = [
        ["Código", "Cliente", "Teléfono", "Marca", "Descripcion", "Entrada", "Entrega", "Técnico", "Precio"]
    ]
    
    # Agregar cada reparación a la tabla
    for rep in reparaciones:
        # Convertir valores a Paragraph para permitir envolturas automáticas
        codigo = Paragraph(str(rep.codigo_orden), cell_style)
        cliente = Paragraph(f"{rep.cliente.nombre} {rep.cliente.apellido}" if rep.cliente else "N/A", cell_style)
        telefono = Paragraph(rep.cliente.telefono if rep.cliente else "N/A", cell_style)
        marca = Paragraph(rep.marca_reloj, cell_style)
        
        # La descripción como Paragraph permitirá ajuste automático
        descripcion = Paragraph(rep.descripcion, cell_style)
        
        fecha_ingreso = Paragraph(rep.fecha_ingreso.strftime('%d/%m/%Y'), cell_style)
        fecha_estimada = Paragraph(rep.fecha_entrega_estimada.strftime('%d/%m/%Y') if rep.fecha_entrega_estimada else "N/A", cell_style)
        tecnico = Paragraph(rep.tecnico.nombre, cell_style)
        precio = Paragraph(f"${rep.precio:,.2f}", cell_style)
        
        table_data.append([
            codigo, cliente, telefono, marca, descripcion, 
            fecha_ingreso, fecha_estimada, tecnico, precio
        ])
    
    # Ancho de columnas
    col_widths = [0.7*inch, 1.5*inch, 0.9*inch, 0.7*inch, 1.5*inch, 0.8*inch, 0.8*inch, 1.1*inch, 0.8*inch]

    
    # Crear la tabla
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Estilo de la tabla
    table_style = TableStyle([
        # Estilo de encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d4e484')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        
        # Estilo del cuerpo
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        
        # Alineación para la columna de precios
        ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
        
        # Borde para todas las celdas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    
    # Aplicar el estilo a la tabla
    table.setStyle(table_style)
    elements.append(table)
    
    # Agregar pie de página
    elements.append(Spacer(1, 0.25*inch))
    
    # Información de generación del reporte
    footer_text = f"Generado el {timezone.now().strftime('%d/%m/%Y %H:%M')}"
    elements.append(Paragraph(footer_text, normal_style))
    elements.append(Paragraph("Este documento es un reporte oficial de ServiWatch", normal_style))
    
    # Construir el PDF
    doc.build(elements)
    
    # Obtener el valor del PDF del buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf