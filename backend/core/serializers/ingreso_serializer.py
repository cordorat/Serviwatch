from rest_framework import serializers
from core.models.ingreso import Ingreso
from datetime import date


class IngresoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Ingreso.
    Maneja la serialización y deserialización de registros de ingresos financieros.
    """
    
    # Campo calculado para mostrar si es del mes actual
    es_mes_actual = serializers.SerializerMethodField()
    
    class Meta:
        model = Ingreso
        fields = ['id', 'fecha', 'valor', 'descripcion', 'es_mes_actual']
        read_only_fields = ['id']
    
    def get_es_mes_actual(self, obj):
        """Verifica si el ingreso es del mes actual."""
        if obj.fecha:
            today = date.today()
            return obj.fecha.year == today.year and obj.fecha.month == today.month
        return False
    
    def validate_valor(self, value):
        """Validación para el valor del ingreso."""
        if value <= 0:
            raise serializers.ValidationError("El valor del ingreso debe ser mayor a cero.")
        return value
    
    def validate_descripcion(self, value):
        """Validación para la descripción."""
        if len(value) > 100:
            raise serializers.ValidationError("La descripción debe tener máximo 100 caracteres.")
        if not value.strip():
            raise serializers.ValidationError("La descripción no puede estar vacía.")
        return value
    
    def validate_fecha(self, value):
        """Validación para la fecha."""
        if value > date.today():
            raise serializers.ValidationError("La fecha no puede ser futura.")
        return value
