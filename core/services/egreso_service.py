from core.models import Egreso
import locale
def get_all_egreso():
    return Egreso.objects.all()

def crear_egreso(datos):
    egreso = Egreso(
        fecha=datos['fecha'],
        valor=datos['valor'],
        descripcion=datos['descripcion']
    )
    egreso.save()
    return egreso
def obtener_datos_resumen(datos):
    """Formatea los datos para mostrar en la confirmación"""
    # Configurar locale para formato de moneda de manera segura
    try:
        locale.setlocale(locale.LC_ALL, '')
    except:
        pass


    try:
        valor_formateada = locale.currency(float(datos['valor']), grouping=True)
    except:
        valor_formateada = f"${float(datos['valor']):,.2f}"

    return {
        'fecha': datos['fecha'].strftime('%d/%m/%Y'),
        'valor': valor_formateada,
        'descripcion': datos['descripcion']
    }