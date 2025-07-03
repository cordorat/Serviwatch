from core.models.reloj import Reloj
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from django.utils import timezone

def get_all_relojes():
    return Reloj.objects.all()

def create_reloj(form):
    reloj = form.save(commit=False)
    precio = form.cleaned_data.get('precio')
    tiene_comision = form.cleaned_data.get('tiene_comision')

    try:
        comision = int(precio) * 0.2 if tiene_comision else 0
    except Exception:
        comision = 0
    reloj.comision = str(int(comision))

    reloj.saldo_pendiente = str(precio)
    reloj.pagado = False

    reloj.save()
    return reloj

DATOS_CONST = 'Sin datos'

def generar_pdf_relojes(relojes, filtro_estado, filtro_tipo, request=None):
    """
    Genera un PDF con el listado de relojes filtrados.
    
    Args:
        relojes: QuerySet de relojes
        filtro_estado: Estado usado para filtrar (o 'todos')
        filtro_tipo: Tipo usado para filtrar (o 'todos')
        request: Objeto request para acceder a información del usuario
    
    Returns:
        BytesIO con el contenido del PDF
    """
    # Configurar el buffer y el documento
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
        title=f"Reporte de Relojes - {filtro_estado if filtro_estado != 'todos' else 'Todos los estados'}"
    )
    
    # Lista para almacenar todos los elementos del PDF
    elements = []
    
    # Configurar estilos
    styles = getSampleStyleSheet()
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Heading2'],
        alignment=1,  # Centrado
        spaceAfter=2,
        textColor=colors.black
    )
    normal_style = styles['Normal']
    
    # Intentar incluir el logo si está disponible
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
    #elements.append(Paragraph("ServiWatch", title_style))
    elements.append(Paragraph("Calle 25 Norte # 5 an -17", normal_style))
    elements.append(Paragraph("Tel: 555-1234", normal_style))
    elements.append(Spacer(1, 0.05*inch))
    
    # Título principal
    titulo = "REPORTE DE REPARACIONES"
    elements.append(Paragraph(titulo, subtitle_style))

    elements.append(Spacer(1, 0.25*inch))
    
    # Subtítulo con filtros aplicados
    filtros_texto = []
    if filtro_estado and filtro_estado != 'todos':
        filtros_texto.append(f"Estado: {filtro_estado}")
    if filtro_tipo and filtro_tipo != 'todos':
        filtros_texto.append(f"Tipo: {filtro_tipo}")
    
    if filtros_texto:
        subtitle_text = f"Filtros aplicados: {', '.join(filtros_texto)}"
    else:
        subtitle_text = "Todos los relojes"
    
    subtitle = Paragraph(subtitle_text, subtitle_style)
    elements.append(subtitle)

    elements.append(Spacer(1, 0.25*inch))
    
      # Crear datos para la tabla
    data = [['Marca', 'Referencia', 'Precio', 'Tipo', 'Dueño']]
    
    for reloj in relojes:
        # Formatear el precio correctamente
        precio_formateado = "N/A"
        if reloj.precio:
            try:
                precio_num = int(reloj.precio)
                precio_formateado = f"${precio_num:,}"
            except (ValueError, TypeError):
                precio_formateado = f"${reloj.precio}"
        
        fila = [
            reloj.marca or "N/A",
            reloj.referencia or "N/A", 
            precio_formateado,
            reloj.get_tipo_display() or "N/A",
            reloj.dueno or "Sin dueño"
        ]
        data.append(fila)
    
    # Si no hay datos, mostrar mensaje
    if len(data) == 1:  # Solo encabezados
        data.append([DATOS_CONST, DATOS_CONST, DATOS_CONST, DATOS_CONST, DATOS_CONST])
    
    # Crear la tabla
    table = Table(data, colWidths=[1.5*inch, 1.8*inch, 1.2*inch, 1.2*inch, 2*inch])
      # Estilo de la tabla
    table_style = TableStyle([
        # Estilo de encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d4e484')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        
        # Estilo del cuerpo - todas las columnas alineadas a la izquierda
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        
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
    
    # Obtener el valor del buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf