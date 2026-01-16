from rest_framework import serializers
from core.models.cambiar_contraseña import PasswordResetToken
from django.contrib.auth import get_user_model

User = get_user_model()


class PasswordResetTokenSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo PasswordResetToken.
    Maneja la serialización de tokens de recuperación de contraseña.
    """
    
    # Información del usuario (solo lectura)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    
    # Campo calculado para verificar validez
    is_valid_token = serializers.SerializerMethodField()
    
    class Meta:
        model = PasswordResetToken
        fields = [
            'id', 'user', 'username', 'email', 
            'token', 'created_at', 'used', 'is_valid_token'
        ]
        read_only_fields = ['id', 'created_at', 'username', 'email', 'is_valid_token']
    
    def get_is_valid_token(self, obj):
        """Verifica si el token es válido (no usado y no expirado)."""
        return obj.is_valid()
