from core.models.abono import Abono
from core.models.reloj import Reloj

def get_all_abonos(reloj_id):
    """Obtiene todos los abonos de un reloj específico"""
    return Abono.objects.filter(reloj_id=reloj_id).order_by('-fecha')

def calcular_saldo_pendiente(reloj, monto_abono=None):
    """Calcula el saldo pendiente después de un abono"""
    try:
        precio = int(reloj.precio)
        saldo_actual = int(reloj.saldo_pendiente)
        
        if monto_abono:
            monto = int(monto_abono)
            nuevo_saldo = str(max(0, saldo_actual - monto))
        else:
            nuevo_saldo = str(precio)
            
        return nuevo_saldo
    except (ValueError, TypeError):
        return '0'

def registrar_abono(reloj_id, monto, descripcion=""):
    """
    Registra un nuevo abono y actualiza el saldo pendiente del reloj
    """
    try:
        reloj = Reloj.objects.get(id=reloj_id)
        
        if reloj.metodo_pago != 'ABONO':
            raise ValueError("Este reloj no está configurado para pagos por abonos")

        # Asegurarse de que haya un saldo pendiente inicial
        if not reloj.saldo_pendiente:
            reloj.saldo_pendiente = reloj.precio
            reloj.save()

        # Convertir valores a enteros para cálculos
        try:
            saldo_actual = int(reloj.saldo_pendiente)
            monto_abono = int(monto)
        except ValueError:
            raise ValueError("Error al convertir valores numéricos")

        # Validar monto del abono
        if monto_abono <= 0:
            raise ValueError("El monto del abono debe ser mayor a 0")
        
        if monto_abono > saldo_actual:
            raise ValueError(f"El monto del abono ({monto_abono}) no puede ser mayor al saldo pendiente ({saldo_actual})")

        # Crear el registro de abono
        abono = Abono.objects.create(
            reloj=reloj,
            monto=str(monto_abono),
            descripcion=descripcion
        )

        # Actualizar saldo pendiente y estado de pago
        nuevo_saldo = saldo_actual - monto_abono
        reloj.saldo_pendiente = str(nuevo_saldo)
        
        if nuevo_saldo == 0:
            reloj.pagado = True
        
        reloj.save()
        
        print(f"Abono registrado - ID: {abono.id}, Monto: {monto_abono}, Nuevo saldo: {nuevo_saldo}")
        return abono, reloj

    except Reloj.DoesNotExist:
        raise ValueError(f"No se encontró el reloj con ID {reloj_id}")
    except Exception as e:
        print(f"Error al registrar abono: {str(e)}")
        raise