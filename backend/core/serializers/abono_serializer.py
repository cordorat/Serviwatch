from rest_framework import serializers
from core.models.abono import Abono
from core.models.reloj import Reloj


class AbonoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Abono.
    Maneja la serialización y deserialización de abonos a relojes.
    """
    
    # Información del reloj para lectura
    reloj_info = serializers.SerializerMethodField()
    
    # ID del reloj para escritura
    reloj = serializers.PrimaryKeyRelatedField(
        queryset=Reloj.objects.all()
    )
    
    # Campo calculado para el monto como entero
    monto_numerico = serializers.SerializerMethodField()
    
    class Meta:
        model = Abono
        fields = [
            'id', 'reloj', 'reloj_info', 'monto', 'monto_numerico',
            'fecha', 'descripcion'
        ]
        read_only_fields = ['id', 'fecha']
    
    def get_reloj_info(self, obj):
        """Retorna información básica del reloj."""
        if obj.reloj:
            return {
                'id': obj.reloj.id,
                'marca': obj.reloj.marca,
                'referencia': obj.reloj.referencia,
                'precio': obj.reloj.precio,
                'saldo_pendiente': obj.reloj.saldo_pendiente,
                'cliente': f"{obj.reloj.cliente.nombre} {obj.reloj.cliente.apellido}" if obj.reloj.cliente else None
            }
        return None
    
    def get_monto_numerico(self, obj):
        """Retorna el monto como entero."""
        try:
            return int(obj.monto) if obj.monto else 0
        except (ValueError, TypeError):
            return 0
    
    def validate_monto(self, value):
        """Validación para el monto."""
        if not value.isdigit():
            raise serializers.ValidationError("El monto debe ser un número válido.")
        if len(value) > 20:
            raise serializers.ValidationError("El monto debe tener máximo 20 caracteres.")
        if int(value) <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a cero.")
        return value
    
    def validate_reloj(self, value):
        """Validación para el reloj."""
        if value.estado != 'VENDIDO':
            raise serializers.ValidationError(
                "Solo se pueden registrar abonos para relojes vendidos."
            )
        if value.pagado:
            raise serializers.ValidationError(
                "Este reloj ya está completamente pagado."
            )
        return value
    
    def validate(self, data):
        """Validaciones a nivel de objeto."""
        reloj = data.get('reloj')
        monto = data.get('monto')
        
        if reloj and monto:
            try:
                monto_int = int(monto)
                saldo_pendiente = int(reloj.saldo_pendiente) if reloj.saldo_pendiente else 0
                
                if monto_int > saldo_pendiente:
                    raise serializers.ValidationError({
                        'monto': f'El monto del abono (${monto_int}) no puede ser mayor al saldo pendiente (${saldo_pendiente}).'
                    })
            except (ValueError, TypeError):
                raise serializers.ValidationError({
                    'monto': 'Error al validar el monto del abono.'
                })
        
        return data


class AbonoListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar abonos.
    """
    
    reloj_marca = serializers.CharField(source='reloj.marca', read_only=True)
    reloj_referencia = serializers.CharField(source='reloj.referencia', read_only=True)
    monto_numerico = serializers.SerializerMethodField()
    
    class Meta:
        model = Abono
        fields = [
            'id', 'reloj', 'reloj_marca', 'reloj_referencia',
            'monto', 'monto_numerico', 'fecha', 'descripcion'
        ]
    
    def get_monto_numerico(self, obj):
        """Retorna el monto como entero."""
        try:
            return int(obj.monto) if obj.monto else 0
        except (ValueError, TypeError):
            return 0
