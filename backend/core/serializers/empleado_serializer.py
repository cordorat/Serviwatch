from rest_framework import serializers
from core.models.empleado import Empleado
from datetime import date


class EmpleadoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Empleado.
    Maneja la serialización y deserialización de objetos Empleado.
    """
    
    # Campo calculado para mostrar el nombre completo
    nombre_completo = serializers.SerializerMethodField()
    
    # Campo calculado para mostrar la edad
    edad = serializers.SerializerMethodField()
    
    # Campo calculado para mostrar años de servicio
    anios_servicio = serializers.SerializerMethodField()
    
    # Campos con formato legible para choices
    cargo_display = serializers.CharField(source='get_cargo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Empleado
        fields = [
            'id', 'cedula', 'nombre', 'apellidos', 'nombre_completo',
            'fecha_ingreso', 'fecha_nacimiento', 'edad', 'anios_servicio',
            'celular', 'cargo', 'cargo_display', 'salario', 
            'estado', 'estado_display'
        ]
        read_only_fields = ['id']
    
    def get_nombre_completo(self, obj):
        """Retorna el nombre completo del empleado."""
        return f"{obj.nombre} {obj.apellidos}"
    
    def get_edad(self, obj):
        """Calcula la edad del empleado."""
        if obj.fecha_nacimiento:
            today = date.today()
            edad = today.year - obj.fecha_nacimiento.year
            # Ajustar si aún no ha cumplido años este año
            if today.month < obj.fecha_nacimiento.month or \
               (today.month == obj.fecha_nacimiento.month and today.day < obj.fecha_nacimiento.day):
                edad -= 1
            return edad
        return None
    
    def get_anios_servicio(self, obj):
        """Calcula los años de servicio del empleado."""
        if obj.fecha_ingreso:
            today = date.today()
            anios = today.year - obj.fecha_ingreso.year
            # Ajustar si aún no ha cumplido el aniversario este año
            if today.month < obj.fecha_ingreso.month or \
               (today.month == obj.fecha_ingreso.month and today.day < obj.fecha_ingreso.day):
                anios -= 1
            return anios
        return None
    
    def validate_cedula(self, value):
        """
        Validación adicional para la cédula.
        Verifica que contenga solo números y tenga máximo 10 dígitos.
        """
        if not value.isdigit():
            raise serializers.ValidationError("La cédula debe contener solo números.")
        if len(value) > 10:
            raise serializers.ValidationError("La cédula debe tener máximo 10 dígitos.")
        
        # Verificar que no exista otra cédula igual (excepto en update)
        instance = self.instance
        if Empleado.objects.filter(cedula=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Ya existe un empleado con esta cédula.")
        
        return value
    
    def validate_celular(self, value):
        """
        Validación adicional para el celular.
        Verifica que comience con 3 y tenga exactamente 10 dígitos.
        """
        if not value.isdigit():
            raise serializers.ValidationError("El número de celular debe contener solo números.")
        if len(value) != 10:
            raise serializers.ValidationError("El número de celular debe tener exactamente 10 dígitos.")
        if not value.startswith('3'):
            raise serializers.ValidationError("El número de celular debe comenzar con 3.")
        return value
    
    def validate_nombre(self, value):
        """Validación para el campo nombre."""
        if len(value) > 50:
            raise serializers.ValidationError("El nombre debe tener máximo 50 caracteres.")
        return value
    
    def validate_apellidos(self, value):
        """Validación para el campo apellidos."""
        if len(value) > 50:
            raise serializers.ValidationError("Los apellidos deben tener máximo 50 caracteres.")
        return value
    
    def validate_salario(self, value):
        """Validación para el salario."""
        if not value.isdigit():
            raise serializers.ValidationError("El salario debe ser numérico.")
        if int(value) <= 0:
            raise serializers.ValidationError("El salario debe ser mayor a 0.")
        return value
    
    def validate_fecha_nacimiento(self, value):
        """Validación para la fecha de nacimiento."""
        if value > date.today():
            raise serializers.ValidationError("La fecha de nacimiento no puede ser futura.")
        
        # Calcular edad mínima (debe tener al menos 18 años)
        edad = date.today().year - value.year
        if date.today().month < value.month or \
           (date.today().month == value.month and date.today().day < value.day):
            edad -= 1
        
        if edad < 18:
            raise serializers.ValidationError("El empleado debe tener al menos 18 años.")
        
        return value
    
    def validate_fecha_ingreso(self, value):
        """Validación para la fecha de ingreso."""
        if value > date.today():
            raise serializers.ValidationError("La fecha de ingreso no puede ser futura.")
        return value
    
    def validate(self, data):
        """
        Validaciones a nivel de objeto (múltiples campos).
        """
        # Si estamos creando o actualizando, verificar fechas
        fecha_nacimiento = data.get('fecha_nacimiento', self.instance.fecha_nacimiento if self.instance else None)
        fecha_ingreso = data.get('fecha_ingreso', self.instance.fecha_ingreso if self.instance else None)
        
        if fecha_nacimiento and fecha_ingreso:
            # El empleado debe haber nacido antes de ingresar
            if fecha_nacimiento >= fecha_ingreso:
                raise serializers.ValidationError({
                    'fecha_ingreso': 'La fecha de ingreso debe ser posterior a la fecha de nacimiento.'
                })
            
            # Calcular edad al momento de ingreso
            edad_ingreso = fecha_ingreso.year - fecha_nacimiento.year
            if fecha_ingreso.month < fecha_nacimiento.month or \
               (fecha_ingreso.month == fecha_nacimiento.month and fecha_ingreso.day < fecha_nacimiento.day):
                edad_ingreso -= 1
            
            if edad_ingreso < 18:
                raise serializers.ValidationError({
                    'fecha_ingreso': 'El empleado debe tener al menos 18 años al momento de ingresar.'
                })
        
        return data
