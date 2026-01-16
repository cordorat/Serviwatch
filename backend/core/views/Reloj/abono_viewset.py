from rest_framework import viewsets, filters, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from core.models.abono import Abono
from core.models.reloj import Reloj
from core.serializers.abono_serializer import AbonoSerializer, AbonoListSerializer
from datetime import date


class AbonoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el modelo Abono.
    Proporciona operaciones CRUD completas para abonos de relojes.
    """
    
    queryset = Abono.objects.all().order_by('-fecha')
    serializer_class = AbonoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['descripcion', 'reloj__marca', 'reloj__referencia']
    ordering_fields = ['fecha', 'monto']
    filterset_fields = ['reloj', 'fecha']
    
    def get_serializer_class(self):
        """Usa un serializer diferente para la lista."""
        if self.action == 'list':
            return AbonoListSerializer
        return AbonoSerializer
    
    def perform_create(self, serializer):
        """
        Override para actualizar el saldo del reloj al crear un abono.
        """
        abono = serializer.save()
        reloj = abono.reloj
        
        try:
            monto = int(abono.monto)
            saldo_actual = int(reloj.saldo_pendiente) if reloj.saldo_pendiente else 0
            nuevo_saldo = saldo_actual - monto
            
            reloj.saldo_pendiente = str(max(0, nuevo_saldo))
            
            # Si el saldo llega a cero, marcar como pagado
            if nuevo_saldo <= 0:
                reloj.pagado = True
            
            reloj.save()
        except (ValueError, TypeError) as e:
            raise serializers.ValidationError(f"Error al actualizar el saldo: {str(e)}")
    
    @action(detail=False, methods=['get'])
    def por_reloj(self, request):
        """
        Endpoint para obtener abonos de un reloj específico.
        GET /api/abonos/por_reloj/?reloj_id=1
        """
        reloj_id = request.query_params.get('reloj_id')
        
        if not reloj_id:
            return Response(
                {'error': 'El parámetro reloj_id es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        abonos = self.queryset.filter(reloj_id=reloj_id)
        serializer = self.get_serializer(abonos, many=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mes_actual(self, request):
        """
        Endpoint para obtener abonos del mes actual.
        GET /api/abonos/mes_actual/
        """
        today = date.today()
        abonos = self.queryset.filter(
            fecha__year=today.year,
            fecha__month=today.month
        )
        serializer = self.get_serializer(abonos, many=True)
        return Response(serializer.data)
