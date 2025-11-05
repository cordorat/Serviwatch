from rest_framework import serializers
from core.models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Cliente.
    Maneja la serialización y deserialización de objetos Cliente.
    """
    
    # Campo calculado para mostrar el nombre completo
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'apellido', 'telefono', 'nombre_completo']
        read_only_fields = ['id']
    
    def get_nombre_completo(self, obj):
        """Retorna el nombre completo del cliente."""
        return f"{obj.nombre} {obj.apellido}"
    
    def validate_telefono(self, value):
        """
        Validación adicional para el teléfono.
        Verifica que contenga solo números y tenga exactamente 10 dígitos.
        """
        if not value.isdigit():
            raise serializers.ValidationError("El teléfono debe contener solo números.")
        if len(value) != 10:
            raise serializers.ValidationError("El teléfono debe tener exactamente 10 dígitos.")
        return value
    
    def validate_nombre(self, value):
        """Validación para el campo nombre."""
        if len(value) > 20:
            raise serializers.ValidationError("El nombre debe tener máximo 20 caracteres.")
        return value
    
    def validate_apellido(self, value):
        """Validación para el campo apellido."""
        if len(value) > 30:
            raise serializers.ValidationError("El apellido debe tener máximo 30 caracteres.")
        return value