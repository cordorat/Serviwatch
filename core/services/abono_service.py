from core.models.abono import Abono
from core.models.reloj import Reloj

def get_all_abonos(reloj_id):
    """Obtiene todos los abonos de un reloj específico"""
    return Abono.objects.filter(reloj_id=reloj_id).order_by('-fecha')

def calcular_saldo_pendiente(reloj, monto_abono=None):
    """Calcula el saldo pendiente después de un abono"""
    try:
        saldo_actual = int(reloj.saldo_pendiente)
        
        if monto_abono:
            nuevo_saldo = saldo_actual - int(monto_abono)
            return str(max(0, nuevo_saldo))
        else:
            return str(saldo_actual)
            
    except (ValueError, TypeError):
        return '0'

def registrar_abono(reloj_id, monto, descripcion=""):
    """Registra un nuevo abono y actualiza el saldo pendiente del reloj"""
    try:
        reloj = Reloj.objects.get(id=reloj_id)
        
        if reloj.metodo_pago != 'ABONO':
            raise ValueError("Solo se pueden registrar abonos para relojes con método de pago ABONO")

        # Asegurarse de que haya un saldo pendiente inicial
        if not reloj.saldo_pendiente:
            reloj.saldo_pendiente = reloj.precio

        # Convertir valores a enteros para cálculos
        try:
            monto_abono = int(monto)
            saldo_actual = int(reloj.saldo_pendiente)
        except ValueError:
            raise ValueError("Valores inválidos para el cálculo")

        # Validar monto del abono
        if monto_abono <= 0:
            raise ValueError("El monto del abono debe ser mayor a 0")
        
        if monto_abono > saldo_actual:
            raise ValueError("El monto del abono no puede ser mayor al saldo pendiente")

        # Calcular nuevo saldo pendiente
        nuevo_saldo = calcular_saldo_pendiente(reloj, monto_abono)
        
        # Crear el abono
        abono = Abono.objects.create(
            reloj=reloj,
            monto=str(monto_abono),
            descripcion=descripcion
        )
        
        # Actualizar el saldo pendiente del reloj
        print(f"Saldo actual: {saldo_actual}, Monto abono: {monto_abono}, Nuevo saldo: {nuevo_saldo}")
        reloj.saldo_pendiente = nuevo_saldo
        reloj.pagado = (nuevo_saldo == '0')
        reloj.save()
        
        return abono, reloj

    except Reloj.DoesNotExist:
        raise ValueError("El reloj especificado no existe")
    except Exception as e:
        raise ValueError(f"Error al registrar el abono: {str(e)}")