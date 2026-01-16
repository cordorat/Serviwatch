from rest_framework import serializers
from core.models.reloj import Reloj
from core.models.cliente import Cliente
from core.serializers.cliente_serializer import ClienteSerializer


class RelojSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Reloj.
    Maneja la serialización y deserialización de objetos Reloj (inventario de relojes).
    """
    
    # Representación anidada del cliente para lectura
    cliente_detalle = ClienteSerializer(source='cliente', read_only=True)
    
    # ID del cliente para escritura (crear/actualizar)
    cliente = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(),
        allow_null=True,
        required=False
    )
    
    # Campos para mostrar valores legibles de choices
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    metodo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)
    
    # Campos calculados
    saldo_restante = serializers.SerializerMethodField()
    porcentaje_pagado = serializers.SerializerMethodField()
    total_abonos = serializers.SerializerMethodField()
    
    class Meta:
        model = Reloj
        fields = [
            'id', 'marca', 'referencia', 'precio', 'tiene_comision', 'comision',
            'dueno', 'descripcion', 'tipo', 'tipo_display', 'estado', 'estado_display',
            'fecha_venta', 'pagado', 'cliente', 'cliente_detalle', 'metodo_pago',
            'metodo_pago_display', 'saldo_pendiente', 'saldo_restante',
            'porcentaje_pagado', 'total_abonos'
        ]
        read_only_fields = ['id', 'comision']
    
    def get_saldo_restante(self, obj):
        """Retorna el saldo pendiente como entero."""
        try:
            return int(obj.saldo_pendiente) if obj.saldo_pendiente else 0
        except (ValueError, TypeError):
            return 0
    
    def get_porcentaje_pagado(self, obj):
        """Calcula el porcentaje pagado del reloj."""
        try:
            precio = int(obj.precio) if obj.precio else 0
            saldo_pendiente = int(obj.saldo_pendiente) if obj.saldo_pendiente else 0
            if precio > 0:
                pagado = precio - saldo_pendiente
                return round((pagado / precio) * 100, 2)
        except (ValueError, TypeError):
            pass
        return 0
    
    def get_total_abonos(self, obj):
        """Calcula el total de abonos realizados."""
        total = 0
        for abono in obj.abonos.all():
            try:
                total += int(abono.monto) if abono.monto else 0
            except (ValueError, TypeError):
                continue
        return total
    
    def validate_precio(self, value):
        """Validación para el precio."""
        if not value.isdigit():
            raise serializers.ValidationError("El precio debe ser un número válido.")
        if len(value) > 20:
            raise serializers.ValidationError("El precio debe tener máximo 20 caracteres.")
        if int(value) <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a cero.")
        return value
    
    def validate_comision(self, value):
        """Validación para la comisión."""
        if value and not value.isdigit():
            raise serializers.ValidationError("La comisión debe ser un número válido.")
        return value
    
    def validate_saldo_pendiente(self, value):
        """Validación para el saldo pendiente."""
        if value and not value.isdigit():
            raise serializers.ValidationError("El saldo pendiente debe ser un número válido.")
        if len(value) > 20:
            raise serializers.ValidationError("El saldo pendiente debe tener máximo 20 caracteres.")
        return value
    
    def validate(self, data):
        """Validaciones a nivel de objeto."""
        # Si el estado es VENDIDO, debe tener cliente
        if data.get('estado') == 'VENDIDO' and not data.get('cliente'):
            raise serializers.ValidationError({
                'cliente': 'Un reloj vendido debe tener un cliente asociado.'
            })
        
        # Si tiene comisión, validar que esté marcado
        if data.get('comision') and int(data.get('comision', '0')) > 0:
            if not data.get('tiene_comision'):
                data['tiene_comision'] = True
        
        return data


class RelojListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar relojes.
    Incluye solo la información esencial para vistas de lista.
    """
    
    cliente_nombre = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Reloj
        fields = [
            'id', 'marca', 'referencia', 'precio', 'tipo', 'tipo_display',
            'estado', 'estado_display', 'fecha_venta', 'cliente_nombre', 'pagado'
        ]
    
    def get_cliente_nombre(self, obj):
        """Retorna el nombre completo del cliente o None."""
        if obj.cliente:
            return f"{obj.cliente.nombre} {obj.cliente.apellido}"
        return None
