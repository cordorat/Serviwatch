from core.services.ingreso_service import (
    obtener_ingresos_rango,
    obtener_total_ingresos_rango,
    obtener_total_ingresos_dia
)
from core.services.egreso_service import (
    obtener_egresos_rango,
    obtener_total_egresos_rango
)
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

formato_fecha = '%d/%m/%Y'


def calcular_ganancia_rango(fecha_inicio, fecha_fin):
    """
    Calcula la ganancia neta (ingresos - egresos) en un rango de fechas
    Reutiliza las funciones existentes de los servicios de ingreso y egreso
    """
    try:
        # Usar las funciones existentes de los servicios
        total_ingresos = obtener_total_ingresos_rango(fecha_inicio, fecha_fin)
        total_egresos = obtener_total_egresos_rango(fecha_inicio, fecha_fin)
        ganancia = total_ingresos - total_egresos
        
        return {
            'total_ingresos': total_ingresos,
            'total_egresos': total_egresos,
            'ganancia_neta': ganancia,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        }
    except (ValidationError, DatabaseError) as e:
        # Capturar excepciones específicas de Django
        raise ValidationError(f"Error al calcular ganancia: {str(e)}")


def obtener_ganancia_hoy():
    """
    Obtiene la ganancia del día actual
    Reutiliza las funciones existentes de los servicios
    """
    hoy = date.today()
    return calcular_ganancia_rango(hoy, hoy)


def generar_pdf_ganancias(fecha_inicio, fecha_fin, datos_ganancia, request):


    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            leftMargin=72,  # 1 pulgada
            rightMargin=72,
            topMargin=72,
            bottomMargin=72,
            title=f"Reporte de Ganancias {fecha_inicio} - {fecha_fin}"
        )
        
        # Lista para almacenar todos los elementos del PDF
        elements = []
        
        # Configurar estilos
        styles = getSampleStyleSheet()
        
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
        except Exception as e:
            # Si hay algún error con el logo, simplemente continuamos sin él
            pass
        
        # Encabezado con datos de la empresa
        elements.append(Paragraph("Calle 25 Norte # 5 an -17", normal_style))
        elements.append(Paragraph("Tel: 555-1234", normal_style))
        elements.append(Spacer(1, 0.5*inch))
        
        # Título del reporte
        elements.append(Paragraph("REPORTE DE GANANCIAS", subtitle_style))
        
        # Período del reporte
        elements.append(Paragraph(
            f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", 
            date_style
        ))
        elements.append(Spacer(1, 0.25*inch))
        
        # Preparar los datos para la tabla
        table_data = [
            ["CONCEPTO", "VALOR"]  # Encabezados
        ]
        
        # Agregar filas de datos
        table_data.append([
            "Ingresos Totales",
            f"${datos_ganancia['total_ingresos']:,.2f}"
        ])
        
        table_data.append([
            "Egresos Totales", 
            f"${datos_ganancia['total_egresos']:,.2f}"
        ])
        
        # Fila de ganancia neta con color según si es positiva o negativa
        ganancia_color = colors.green if datos_ganancia['ganancia_neta'] >= 0 else colors.red
        ganancia_texto = f"${datos_ganancia['ganancia_neta']:,.2f}"
        
        table_data.append([
            "GANANCIA NETA:",
            ganancia_texto
        ])
        
        # Crear la tabla con datos
        col_widths = [3*inch, 2*inch]
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
            
            # Estilo para la fila de ganancia neta
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (-1, -1), (-1, -1), ganancia_color),  # Color según ganancia
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
        
    except (OSError, IOError) as e:
        # Errores de archivo/buffer al generar PDF
        raise ValidationError(f"Error al crear el archivo PDF: {str(e)}")
