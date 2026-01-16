from rest_framework import serializers
from core.models.pilas import Pilas


class PilasSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Pilas.
    Maneja la serialización y deserialización de objetos Pilas (inventario).
    """
    
    # Campo calculado para mostrar el valor total del inventario de esta pila
    valor_total = serializers.SerializerMethodField()
    
    class Meta:
        model = Pilas
        fields = ['id', 'codigo', 'precio', 'cantidad', 'valor_total']
        read_only_fields = ['id']
    
    def get_valor_total(self, obj):
        """Calcula el valor total del inventario (precio * cantidad)."""
        try:
            precio = int(obj.precio) if obj.precio else 0
            cantidad = int(obj.cantidad) if obj.cantidad else 0
            return precio * cantidad
        except (ValueError, TypeError):
            return 0
    
    def validate_codigo(self, value):
        """
        Validación para el código de la pila.
        Verifica que no exista otro código igual.
        """
        if len(value) > 30:
            raise serializers.ValidationError("El código debe tener máximo 30 caracteres.")
        
        # Verificar que no exista otra pila con el mismo código
        instance = self.instance
        if Pilas.objects.filter(codigo=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Ya existe una pila con este código.")
        
        return value
    
    def validate_precio(self, value):
        """Validación para el precio."""
        if not value.isdigit():
            raise serializers.ValidationError("El precio debe ser un número válido.")
        if len(value) > 6:
            raise serializers.ValidationError("El precio debe tener máximo 6 caracteres.")
        return value
    
    def validate_cantidad(self, value):
        """Validación para la cantidad."""
        if not value.isdigit():
            raise serializers.ValidationError("La cantidad debe ser un número válido.")
        if len(value) > 3:
            raise serializers.ValidationError("La cantidad debe tener máximo 3 caracteres.")
        if int(value) < 0:
            raise serializers.ValidationError("La cantidad no puede ser negativa.")
        return value
