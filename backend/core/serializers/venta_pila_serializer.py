from rest_framework import serializers
from core.models.VentaPila import VentaPila
from core.models.pilas import Pilas
from core.serializers.pilas_serializer import PilasSerializer


class VentaPilaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo VentaPila.
    Maneja la serialización y deserialización de ventas de pilas.
    """
    
    # Información de la pila para lectura
    pila_detalle = PilasSerializer(source='pila', read_only=True)
    
    # ID de la pila para escritura
    pila = serializers.PrimaryKeyRelatedField(
        queryset=Pilas.objects.all()
    )
    
    # Campo calculado del modelo (property)
    precio_total = serializers.SerializerMethodField()
    
    class Meta:
        model = VentaPila
        fields = [
            'id', 'pila', 'pila_detalle', 'cantidad', 'precio_unitario',
            'fecha_venta', 'precio_total'
        ]
        read_only_fields = ['id', 'fecha_venta']
    
    def get_precio_total(self, obj):
        """Retorna el precio total de la venta."""
        return obj.precio_total
    
    def validate_cantidad(self, value):
        """Validación para la cantidad."""
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a cero.")
        return value
    
    def validate_precio_unitario(self, value):
        """Validación para el precio unitario."""
        if value < 0:
            raise serializers.ValidationError("El precio unitario no puede ser negativo.")
        return value
    
    def validate(self, data):
        """Validaciones a nivel de objeto."""
        pila = data.get('pila')
        cantidad = data.get('cantidad')
        
        if pila and cantidad:
            # Verificar que haya suficiente stock
            try:
                stock_disponible = int(pila.cantidad) if pila.cantidad else 0
                
                # Si es una actualización, sumar la cantidad anterior al stock
                if self.instance:
                    stock_disponible += self.instance.cantidad
                
                if cantidad > stock_disponible:
                    raise serializers.ValidationError({
                        'cantidad': f'No hay suficiente stock. Disponible: {stock_disponible} unidades.'
                    })
            except (ValueError, TypeError):
                raise serializers.ValidationError({
                    'cantidad': 'Error al validar el stock disponible.'
                })
        
        # Si no se especifica precio unitario, usar el de la pila
        if pila and 'precio_unitario' not in data:
            try:
                data['precio_unitario'] = int(pila.precio) if pila.precio else 0
            except (ValueError, TypeError):
                data['precio_unitario'] = 0
        
        return data
    
    def create(self, validated_data):
        """
        Override del método create para actualizar el stock de la pila.
        """
        pila = validated_data['pila']
        cantidad = validated_data['cantidad']
        
        # Reducir el stock de la pila
        try:
            stock_actual = int(pila.cantidad) if pila.cantidad else 0
            nuevo_stock = stock_actual - cantidad
            pila.cantidad = str(nuevo_stock)
            pila.save()
        except (ValueError, TypeError):
            raise serializers.ValidationError("Error al actualizar el stock de la pila.")
        
        # Crear la venta
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Override del método update para ajustar el stock correctamente.
        """
        pila = validated_data.get('pila', instance.pila)
        nueva_cantidad = validated_data.get('cantidad', instance.cantidad)
        cantidad_anterior = instance.cantidad
        
        # Calcular la diferencia de cantidad
        diferencia = nueva_cantidad - cantidad_anterior
        
        if diferencia != 0:
            try:
                stock_actual = int(pila.cantidad) if pila.cantidad else 0
                nuevo_stock = stock_actual - diferencia
                
                if nuevo_stock < 0:
                    raise serializers.ValidationError({
                        'cantidad': 'No hay suficiente stock para esta actualización.'
                    })
                
                pila.cantidad = str(nuevo_stock)
                pila.save()
            except (ValueError, TypeError):
                raise serializers.ValidationError("Error al actualizar el stock de la pila.")
        
        return super().update(instance, validated_data)


class VentaPilaListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar ventas de pilas.
    """
    
    pila_codigo = serializers.CharField(source='pila.codigo', read_only=True)
    precio_total = serializers.SerializerMethodField()
    
    class Meta:
        model = VentaPila
        fields = [
            'id', 'pila', 'pila_codigo', 'cantidad',
            'precio_unitario', 'fecha_venta', 'precio_total'
        ]
    
    def get_precio_total(self, obj):
        """Retorna el precio total de la venta."""
        return obj.precio_total
