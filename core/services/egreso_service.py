
from core.models.egreso import Egreso
from django.db.models import Sum
from datetime import date
from django.core.exceptions import ValidationError
from django.db.utils import DatabaseError
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.utils import timezone
from datetime import datetime

formato_fecha = '%d/%m/%Y'

def crear_egreso(datos):
    try:
        # Verificar que todos los datos necesarios estén presentes
        required_keys = ['fecha', 'valor', 'descripcion']
        for key in required_keys:
            if key not in datos:
                raise ValidationError(f"Falta el dato requerido: {key}")

        # Crear una instancia de Egreso
        egreso = Egreso(
            fecha=datos['fecha'],
            valor=datos['valor'],
            descripcion=datos['descripcion']
        )
        # Guardar el egreso en la base de datos
        egreso.save()
        return egreso

    except ValidationError as ve:
        # Manejar errores de validación
        raise ve
    except Exception as e:
        # Manejar cualquier otro tipo de error
        raise DatabaseError(f"Error al crear el egreso: {str(e)}")
    
    
def obtener_total_egresos_dia(fecha=None):
    """
    Obtiene todos los egresos registrados en una fecha específica.
    Si no se proporciona fecha, usa la fecha actual.
    """
    if fecha is None:
        fecha = date.today()

    total = Egreso.objects.filter(fecha=fecha).aggregate(total=Sum('valor'))['total']
    return total or 0

#--------------------REPORTE DE EGRESOS--------------------#


def obtener_egresos_rango(fecha_inicio, fecha_fin):

    return Egreso.objects.filter(
        fecha__range=(fecha_inicio, fecha_fin)
    ).order_by('fecha')


def obtener_total_egresos_rango(fecha_inicio, fecha_fin):

    total = Egreso.objects.filter(
        fecha__range=(fecha_inicio, fecha_fin)
    ).aggregate(total=Sum('valor'))['total']
    return total or 0

#--------------------GENERAR PDF DE EGRESOS--------------------#

def generar_pdf_egresos(egresos, fecha_inicio, fecha_fin, total, request=None):
    """
    Genera un archivo PDF con el reporte de egresos usando ReportLab.
    
    Args:
        egresos: QuerySet con los egresos a incluir en el reporte
        fecha_inicio: Fecha de inicio del periodo (objeto date)
        fecha_fin: Fecha de fin del periodo (objeto date)
        total: Valor total de los egresos
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
        title=f"Reporte de Egresos {fecha_inicio} - {fecha_fin}"
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
    elements.append(Paragraph("REPORTE DE EGRESOS", subtitle_style))
    
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
    
    # Agregar cada egreso a la tabla
    for egreso in egresos:
        table_data.append([
            egreso.fecha.strftime('%d/%m/%Y'),
            egreso.descripcion,
            f"${egreso.valor:,.2f}"
        ])
    
    # Si no hay egresos, mostrar un mensaje
    if not egresos:
        table_data.append(["", "No hay egresos registrados en este período", ""])
    
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
    """Extrae la lógica de parseo de fecha en diferentes formatos."""
    formatos = ['%Y-%m-%d', formato_fecha, '%d-%m-%Y']
    
    for formato in formatos:
        try:
            return datetime.strptime(fecha_str, formato).date()
        except ValueError:
            continue
    
    # Si ningún formato funciona, lanzamos error
    raise ValueError(f"Formato de fecha no reconocido: {fecha_str}")


def _crear_egreso_y_responder(request, datos):
    """Extrae la lógica de crear un egreso y generar la respuesta apropiada."""
    # Guarda en la base de datos
    crear_egreso(datos)
    
    # Mensaje de éxito
    messages.success(request, "Egreso ingresado con éxito")
    
    # Limpia la sesión
    del request.session['egreso_data']
    
    # Maneja el tipo de respuesta según la solicitud
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': "Egreso ingresado con éxito"
        })
    
    return redirect('egreso')