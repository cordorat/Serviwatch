from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from core.models.reparacion import Reparacion
from core.serializers.reparacion_serializer import ReparacionSerializer, ReparacionListSerializer
from datetime import date


class ReparacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el modelo Reparacion.
    Proporciona operaciones CRUD completas para órdenes de reparación.
    """
    
    queryset = Reparacion.objects.all().select_related('cliente', 'tecnico').order_by('-fecha_ingreso')
    serializer_class = ReparacionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo_orden', 'marca_reloj', 'cliente__nombre', 'cliente__apellido']
    ordering_fields = ['fecha_ingreso', 'fecha_entrega_estimada', 'precio', 'estado']
    filterset_fields = ['estado', 'tecnico', 'cliente', 'mantenimiento']
    
    def get_serializer_class(self):
        """Usa un serializer diferente para la lista."""
        if self.action == 'list':
            return ReparacionListSerializer
        return ReparacionSerializer
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """
        Endpoint para obtener reparaciones pendientes (no entregadas).
        GET /api/reparaciones/pendientes/
        """
        reparaciones = self.queryset.exclude(estado='Entregado')
        serializer = ReparacionListSerializer(reparaciones, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def retrasadas(self, request):
        """
        Endpoint para obtener reparaciones retrasadas.
        GET /api/reparaciones/retrasadas/
        """
        today = date.today()
        reparaciones = self.queryset.filter(
            fecha_entrega_estimada__lt=today
        ).exclude(estado='Entregado')
        
        serializer = ReparacionListSerializer(reparaciones, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_tecnico(self, request):
        """
        Endpoint para obtener reparaciones de un técnico específico.
        GET /api/reparaciones/por_tecnico/?tecnico_id=1
        """
        tecnico_id = request.query_params.get('tecnico_id')
        
        if not tecnico_id:
            return Response(
                {'error': 'El parámetro tecnico_id es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reparaciones = self.queryset.filter(tecnico_id=tecnico_id)
        serializer = self.get_serializer(reparaciones, many=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_estado(self, request):
        """
        Endpoint para obtener reparaciones agrupadas por estado.
        GET /api/reparaciones/por_estado/
        """
        estados = {}
        for estado_key, estado_label in Reparacion.ESTADOS:
            count = self.queryset.filter(estado=estado_key).count()
            estados[estado_key] = {
                'label': estado_label,
                'count': count
            }
        
        return Response(estados)
    
    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        """
        Endpoint para cambiar el estado de una reparación.
        PATCH /api/reparaciones/{id}/cambiar_estado/
        Body: {"estado": "Reparación", "tecnico": 1}
        """
        reparacion = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if not nuevo_estado:
            return Response(
                {'error': 'El campo estado es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que el estado sea válido
        estados_validos = [e[0] for e in Reparacion.ESTADOS]
        if nuevo_estado not in estados_validos:
            return Response(
                {'error': f'Estado inválido. Opciones: {", ".join(estados_validos)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Si requiere técnico, validar
        estados_requieren_tecnico = ['Reparación', 'Prueba', 'Listo', 'Entregado']
        if nuevo_estado in estados_requieren_tecnico and not reparacion.tecnico:
            tecnico_id = request.data.get('tecnico')
            if not tecnico_id:
                return Response(
                    {'error': f'El estado "{nuevo_estado}" requiere asignar un técnico.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            from core.models.empleado import Empleado
            try:
                tecnico = Empleado.objects.get(pk=tecnico_id, cargo='Técnico', estado='Activo')
                reparacion.tecnico = tecnico
            except Empleado.DoesNotExist:
                return Response(
                    {'error': 'Técnico no encontrado o no está activo.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        reparacion.estado = nuevo_estado
        reparacion.save()
        
        serializer = self.get_serializer(reparacion)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def asignar_tecnico(self, request, pk=None):
        """
        Endpoint para asignar un técnico a una reparación.
        PATCH /api/reparaciones/{id}/asignar_tecnico/
        Body: {"tecnico": 1}
        """
        reparacion = self.get_object()
        tecnico_id = request.data.get('tecnico')
        
        if not tecnico_id:
            return Response(
                {'error': 'El campo tecnico es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from core.models.empleado import Empleado
        try:
            tecnico = Empleado.objects.get(pk=tecnico_id, cargo='Técnico', estado='Activo')
            reparacion.tecnico = tecnico
            reparacion.save()
            
            serializer = self.get_serializer(reparacion)
            return Response(serializer.data)
        except Empleado.DoesNotExist:
            return Response(
                {'error': 'Técnico no encontrado o no está activo.'},
                status=status.HTTP_404_NOT_FOUND
            )
