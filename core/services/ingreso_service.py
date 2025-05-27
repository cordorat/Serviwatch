from core.models.ingreso import Ingreso
from django.db.models import Sum
from datetime import date
from django.core.exceptions import ValidationError
from django.db.utils import DatabaseError
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.utils import timezone
from datetime import datetime
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect

formato_fecha = '%d/%m/%Y'

def crear_ingreso(datos):
    try:
        # Verificar que todos los datos necesarios estén presentes
        required_keys = ['fecha', 'valor', 'descripcion']
        for key in required_keys:
            if key not in datos:
                raise ValidationError(f"Falta el dato requerido: {key}")

        # Crear una instancia de Ingreso
        ingreso = Ingreso(
            fecha=datos['fecha'],
            valor=datos['valor'],
            descripcion=datos['descripcion']
        )
        # Guardar el ingreso en la base de datos
        ingreso.save()
        return ingreso

    except ValidationError as ve:
        # Manejar errores de validación
        raise ve
    except Exception as e:
        # Manejar cualquier otro tipo de error
        raise DatabaseError(f"Error al crear el ingreso: {str(e)}")
    
    
def obtener_total_ingresos_dia(fecha=None):
    """
    Obtiene todos los ingresos registrados en una fecha específica.
    Si no se proporciona fecha, usa la fecha actual.
    """
    if fecha is None:
        fecha = date.today()

    total = Ingreso.objects.filter(fecha=fecha).aggregate(total=Sum('valor'))['total']
    return total or 0

#--------------------REPORTE DE INGRESOS--------------------#


def obtener_ingresos_rango(fecha_inicio, fecha_fin):

    return Ingreso.objects.filter(
        fecha__range=(fecha_inicio, fecha_fin)
    ).order_by('fecha')


def obtener_total_ingresos_rango(fecha_inicio, fecha_fin):

    total = Ingreso.objects.filter(
        fecha__range=(fecha_inicio, fecha_fin)
    ).aggregate(total=Sum('valor'))['total']
    return total or 0

#--------------------GENERAR PDF DE INGRESOS--------------------#

def generar_pdf_ingresos(ingresos, fecha_inicio, fecha_fin, total, request=None):
    """
    Genera un archivo PDF con el reporte de ingresos usando ReportLab.
    
    Args:
        ingresos: QuerySet con los ingresos a incluir en el reporte
        fecha_inicio: Fecha de inicio del periodo (objeto date)
        fecha_fin: Fecha de fin del periodo (objeto date)
        total: Valor total de los ingresos
        request: Objeto request (opcional, para obtener la URL base)
        
    Returns:
        BytesIO con el contenido del PDF
    """
    # Crear un buffer para el PDF
    buffer = BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(
        buffer, 
        #pagesize=landscape(letter), comando para cambiar de orientación la pagina
        pagesize=letter,
        leftMargin=72,  # 1 pulgada
        rightMargin=72,
        topMargin=72,
        bottomMargin=72,
        title=f"Reporte de Ingresos {fecha_inicio} - {fecha_fin}"
    )
    
    # Lista para almacenar todos los elementos del PDF
    elements = []
    
    # Configurar estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        alignment=1,  # Centrado
        spaceAfter=12,
        textColor=colors.black
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Heading2'],
        alignment=1,  # Centrado
        spaceAfter=6,
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
    elements.append(Spacer(1, 0.5*inch))
    
    # Título del reporte
    elements.append(Paragraph("REPORTE DE INGRESOS", subtitle_style))
    
    # Período del reporte
    elements.append(Paragraph(
        f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", 
        date_style
    ))
    elements.append(Spacer(1, 0.25*inch))
    
    # Preparar los datos para la tabla
    table_data = [
        ["Fecha", "Descripción", "Valor"]  # Encabezados
    ]
    
    # Agregar cada ingreso a la tabla
    for ingreso in ingresos:
        table_data.append([
            ingreso.fecha.strftime('%d/%m/%Y'),
            ingreso.descripcion,
            f"${ingreso.valor:,.2f}"
        ])
    
    # Si no hay ingresos, mostrar un mensaje
    if not ingresos:
        table_data.append(["", "No hay ingresos registrados en este período", ""])
    
    # Agregar fila de total
    table_data.append([
        "", 
        "TOTAL:", 
        f"${total:,.2f}"
    ])
    
    # Crear la tabla con datos
    col_widths = [1.2*inch, 3.5*inch, 1.3*inch]
    table = Table(table_data, colWidths=col_widths)
    
    # Estilo de la tabla
    table_style = TableStyle([
        # Estilo de encabezados
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d4e484')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Estilo para el cuerpo de la tabla
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 9),
        ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),  # Alinear valores a la derecha
        
        # Estilo para la fila de total
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
        
        # Borde para todas las celdas
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    
    # Aplicar el estilo a la tabla
    table.setStyle(table_style)
    elements.append(table)
    
    # Agregar pie de página
    elements.append(Spacer(1, 0.5*inch))
    
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

def _parsear_fecha(fecha_str):
    """Función auxiliar para parsear la fecha en diferentes formatos."""
    formatos = ['%Y-%m-%d', '%d-%m-%Y', formato_fecha]
    
    for formato in formatos:
        try:
            return datetime.strptime(fecha_str, formato).date()
        except ValueError:
            continue
    
    # Si ningún formato funciona, lanzamos un error
    raise ValueError(f"No se pudo parsear la fecha: {fecha_str}")

def _formatear_datos_ingreso(ingreso_data):
    """Función auxiliar para formatear los datos del ingreso para la plantilla."""
    fecha_obj = _parsear_fecha(ingreso_data['fecha'])
    fecha_formateada = fecha_obj.strftime(formato_fecha)
    
    return {
        'fecha': fecha_formateada,
        'valor': ingreso_data['valor'],
        'descripcion': ingreso_data['descripcion']
    }

def _procesar_confirmacion(request, ingreso_data):
    """Función auxiliar para procesar la confirmación del ingreso."""
    # Preparar datos para el servicio
    fecha = _parsear_fecha(ingreso_data['fecha'])
    datos = {
        'fecha': fecha,
        'valor': ingreso_data['valor'],
        'descripcion': ingreso_data['descripcion']
    }
    
    # Guarda en la base de datos
    crear_ingreso(datos)
    
    # Mensaje de éxito
    messages.success(request, "Ingreso registrado con éxito")
    
    # Limpia la sesión
    del request.session['ingreso_data']
    
    # Manejar solicitudes AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': "Ingreso registrado con éxito"
        })
    
    # Para solicitudes normales
    return redirect('ingreso')