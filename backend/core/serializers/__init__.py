"""
Serializers de la aplicación Core.
Importa todos los serializers para facilitar su uso.
"""

from core.serializers.cliente_serializer import ClienteSerializer
from core.serializers.empleado_serializer import EmpleadoSerializer

__all__ = [
    'ClienteSerializer',
    'EmpleadoSerializer',
]
