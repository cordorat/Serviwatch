from rest_framework import serializers
from core.models.reparacion import Reparacion
from core.models.cliente import Cliente
from core.models.empleado import Empleado
from core.serializers.cliente_serializer import ClienteSerializer
from core.serializers.empleado_serializer import EmpleadoSerializer
from datetime import date


class ReparacionSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Reparacion.
    Maneja la serialización y deserialización de órdenes de reparación.
    Incluye representación anidada de Cliente y Empleado.
    """
    
    # Representación anidada para lectura
    cliente_detalle = ClienteSerializer(source='cliente', read_only=True)
    tecnico_detalle = EmpleadoSerializer(source='tecnico', read_only=True)
    
    # IDs para escritura (crear/actualizar)
    cliente = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all()
    )
    tecnico = serializers.PrimaryKeyRelatedField(
        queryset=Empleado.objects.filter(cargo='Técnico', estado='Activo'),
        allow_null=True,
        required=False
    )
    
    # Campo calculado para mostrar el estado legible
    estado_display = serializers.CharField(
        source='get_estado_display',
        read_only=True
    )
    
    # Campos calculados
    dias_desde_ingreso = serializers.SerializerMethodField()
    dias_para_entrega = serializers.SerializerMethodField()
    esta_retrasada = serializers.SerializerMethodField()
    
    class Meta:
        model = Reparacion
        fields = [
            'id', 'cliente', 'cliente_detalle', 'marca_reloj', 'descripcion',
            'codigo_orden', 'fecha_ingreso', 'fecha_entrega_estimada', 'precio',
            'espacio_fisico', 'estado', 'estado_display', 'tecnico', 'tecnico_detalle',
            'mantenimiento', 'dias_desde_ingreso', 'dias_para_entrega', 'esta_retrasada'
        ]
        read_only_fields = ['id', 'fecha_ingreso', 'codigo_orden']
    
    def get_dias_desde_ingreso(self, obj):
        """Calcula los días desde que ingresó la reparación."""
        if obj.fecha_ingreso:
            delta = date.today() - obj.fecha_ingreso
            return delta.days
        return 0
    
    def get_dias_para_entrega(self, obj):
        """Calcula los días restantes para la entrega estimada."""
        if obj.fecha_entrega_estimada:
            delta = obj.fecha_entrega_estimada - date.today()
            return delta.days
        return 0
    
    def get_esta_retrasada(self, obj):
        """Determina si la reparación está retrasada."""
        if obj.fecha_entrega_estimada and obj.estado != 'Entregado':
            return date.today() > obj.fecha_entrega_estimada
        return False
    
    def validate_codigo_orden(self, value):
        """Validación para el código de orden."""
        if len(value) > 10:
            raise serializers.ValidationError("El código de orden debe tener máximo 10 caracteres.")
        
        # Verificar que no exista otra reparación con el mismo código
        instance = self.instance
        if Reparacion.objects.filter(codigo_orden=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Ya existe una reparación con este código de orden.")
        
        return value
    
    def validate_marca_reloj(self, value):
        """Validación para la marca del reloj."""
        if len(value) > 30:
            raise serializers.ValidationError("La marca del reloj debe tener máximo 30 caracteres.")
        return value
    
    def validate_descripcion(self, value):
        """Validación para la descripción."""
        if len(value) > 500:
            raise serializers.ValidationError("La descripción debe tener máximo 500 caracteres.")
        if not value.strip():
            raise serializers.ValidationError("La descripción no puede estar vacía.")
        return value
    
    def validate_precio(self, value):
        """Validación para el precio."""
        if value < 0:
            raise serializers.ValidationError("El precio no puede ser negativo.")
        return value
    
    def validate_espacio_fisico(self, value):
        """Validación para el espacio físico."""
        if len(value) > 15:
            raise serializers.ValidationError("El espacio físico debe tener máximo 15 caracteres.")
        return value
    
    def validate_fecha_entrega_estimada(self, value):
        """Validación para la fecha de entrega estimada."""
        # Solo validar si no es una actualización o si la fecha cambió
        if value:
            # La fecha de entrega estimada debe ser posterior a la fecha de ingreso
            if self.instance:
                fecha_ingreso = self.instance.fecha_ingreso
            else:
                fecha_ingreso = date.today()
            
            if value < fecha_ingreso:
                raise serializers.ValidationError(
                    "La fecha de entrega estimada no puede ser anterior a la fecha de ingreso."
                )
        
        return value
    
    def validate(self, data):
        """Validaciones a nivel de objeto."""
        # Si el estado es 'En reparación' o posterior, debe tener técnico asignado
        estados_requieren_tecnico = ['Reparación', 'Prueba', 'Listo', 'Entregado']
        estado = data.get('estado', self.instance.estado if self.instance else None)
        tecnico = data.get('tecnico', self.instance.tecnico if self.instance else None)
        
        if estado in estados_requieren_tecnico and not tecnico:
            raise serializers.ValidationError({
                'tecnico': f'El estado "{estado}" requiere que se asigne un técnico.'
            })
        
        return data


class ReparacionListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar reparaciones.
    Incluye solo la información esencial para vistas de lista.
    """
    
    cliente_nombre = serializers.SerializerMethodField()
    tecnico_nombre = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    esta_retrasada = serializers.SerializerMethodField()
    
    class Meta:
        model = Reparacion
        fields = [
            'id', 'codigo_orden', 'cliente_nombre', 'marca_reloj',
            'fecha_ingreso', 'fecha_entrega_estimada', 'precio',
            'estado', 'estado_display', 'tecnico_nombre', 'mantenimiento',
            'esta_retrasada'
        ]
    
    def get_cliente_nombre(self, obj):
        """Retorna el nombre completo del cliente."""
        if obj.cliente:
            return f"{obj.cliente.nombre} {obj.cliente.apellido}"
        return None
    
    def get_tecnico_nombre(self, obj):
        """Retorna el nombre completo del técnico."""
        if obj.tecnico:
            return f"{obj.tecnico.nombre} {obj.tecnico.apellidos}"
        return "Sin asignar"
    
    def get_esta_retrasada(self, obj):
        """Determina si la reparación está retrasada."""
        if obj.fecha_entrega_estimada and obj.estado != 'Entregado':
            return date.today() > obj.fecha_entrega_estimada
        return False
