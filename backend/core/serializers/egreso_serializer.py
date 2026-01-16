from rest_framework import serializers
from core.models.egreso import Egreso
from datetime import date


class EgresoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Egreso.
    Maneja la serialización y deserialización de registros de egresos financieros.
    """
    
    # Campo calculado para mostrar si es del mes actual
    es_mes_actual = serializers.SerializerMethodField()
    
    class Meta:
        model = Egreso
        fields = ['id', 'fecha', 'valor', 'descripcion', 'es_mes_actual']
        read_only_fields = ['id']
    
    def get_es_mes_actual(self, obj):
        """Verifica si el egreso es del mes actual."""
        if obj.fecha:
            today = date.today()
            return obj.fecha.year == today.year and obj.fecha.month == today.month
        return False
    
    def validate_valor(self, value):
        """Validación para el valor del egreso."""
        if value <= 0:
            raise serializers.ValidationError("El valor del egreso debe ser mayor a cero.")
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
