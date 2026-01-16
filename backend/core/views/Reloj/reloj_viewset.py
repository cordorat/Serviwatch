from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from core.models.reloj import Reloj
from core.serializers.reloj_serializer import RelojSerializer, RelojListSerializer
from datetime import date


class RelojViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el modelo Reloj.
    Proporciona operaciones CRUD completas para el inventario de relojes.
    """
    
    queryset = Reloj.objects.all().order_by('-id')
    serializer_class = RelojSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['marca', 'referencia', 'dueno']
    ordering_fields = ['precio', 'fecha_venta', 'marca']
    filterset_fields = ['tipo', 'estado', 'pagado', 'tiene_comision']
    
    def get_serializer_class(self):
        """Usa un serializer diferente para la lista."""
        if self.action == 'list':
            return RelojListSerializer
        return RelojSerializer
    
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """
        Endpoint para obtener relojes disponibles para venta.
        GET /api/relojes/disponibles/
        """
        relojes = self.queryset.filter(estado='DISPONIBLE')
        serializer = RelojListSerializer(relojes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def vendidos(self, request):
        """
        Endpoint para obtener relojes vendidos.
        GET /api/relojes/vendidos/
        """
        relojes = self.queryset.filter(estado='VENDIDO')
        serializer = RelojListSerializer(relojes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pendientes_pago(self, request):
        """
        Endpoint para obtener relojes vendidos con saldo pendiente.
        GET /api/relojes/pendientes_pago/
        """
        relojes = self.queryset.filter(estado='VENDIDO', pagado=False)
        serializer = self.get_serializer(relojes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def historial_abonos(self, request, pk=None):
        """
        Endpoint para obtener el historial de abonos de un reloj.
        GET /api/relojes/{id}/historial_abonos/
        """
        reloj = self.get_object()
        abonos = reloj.abonos.all().order_by('-fecha')
        
        from core.serializers.abono_serializer import AbonoListSerializer
        serializer = AbonoListSerializer(abonos, many=True)
        
        return Response({
            'reloj': {
                'id': reloj.id,
                'marca': reloj.marca,
                'referencia': reloj.referencia,
                'precio': reloj.precio,
                'saldo_pendiente': reloj.saldo_pendiente,
                'pagado': reloj.pagado
            },
            'abonos': serializer.data
        })
    
    @action(detail=True, methods=['patch'])
    def marcar_vendido(self, request, pk=None):
        """
        Endpoint para marcar un reloj como vendido.
        PATCH /api/relojes/{id}/marcar_vendido/
        Body: {"cliente": 1, "metodo_pago": "CONTADO"}
        """
        reloj = self.get_object()
        
        if reloj.estado == 'VENDIDO':
            return Response(
                {'error': 'Este reloj ya está vendido.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cliente_id = request.data.get('cliente')
        metodo_pago = request.data.get('metodo_pago', 'ABONO')
        
        if not cliente_id:
            return Response(
                {'error': 'El cliente es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from core.models.cliente import Cliente
        try:
            cliente = Cliente.objects.get(pk=cliente_id)
        except Cliente.DoesNotExist:
            return Response(
                {'error': 'Cliente no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        reloj.estado = 'VENDIDO'
        reloj.cliente = cliente
        reloj.metodo_pago = metodo_pago
        reloj.fecha_venta = date.today()
        
        if metodo_pago == 'CONTADO':
            reloj.pagado = True
            reloj.saldo_pendiente = '0'
        
        reloj.save()
        
        serializer = self.get_serializer(reloj)
        return Response(serializer.data)
