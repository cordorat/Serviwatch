from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from core.models.VentaPila import VentaPila
from core.serializers.venta_pila_serializer import VentaPilaSerializer, VentaPilaListSerializer
from datetime import date
from django.db.models import Sum


class VentaPilaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el modelo VentaPila.
    Proporciona operaciones CRUD completas para ventas de pilas.
    """
    
    queryset = VentaPila.objects.all().select_related('pila').order_by('-fecha_venta')
    serializer_class = VentaPilaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['pila__codigo']
    ordering_fields = ['fecha_venta', 'cantidad', 'precio_unitario']
    filterset_fields = ['pila', 'fecha_venta']
    
    def get_serializer_class(self):
        """Usa un serializer diferente para la lista."""
        if self.action == 'list':
            return VentaPilaListSerializer
        return VentaPilaSerializer
    
    @action(detail=False, methods=['get'])
    def mes_actual(self, request):
        """
        Endpoint para obtener ventas del mes actual.
        GET /api/ventas-pilas/mes_actual/
        """
        today = date.today()
        ventas = self.queryset.filter(
            fecha_venta__year=today.year,
            fecha_venta__month=today.month
        )
        serializer = self.get_serializer(ventas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def total_vendido(self, request):
        """
        Endpoint para obtener el total vendido en un período.
        GET /api/ventas-pilas/total_vendido/?fecha_inicio=2024-01-01&fecha_fin=2024-12-31
        """
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        queryset = self.queryset
        
        if fecha_inicio:
            queryset = queryset.filter(fecha_venta__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_venta__lte=fecha_fin)
        
        # Calcular el total
        total = 0
        for venta in queryset:
            total += venta.precio_total
        
        cantidad_ventas = queryset.count()
        cantidad_pilas = queryset.aggregate(total=Sum('cantidad'))['total'] or 0
        
        return Response({
            'total_vendido': total,
            'cantidad_ventas': cantidad_ventas,
            'cantidad_pilas_vendidas': cantidad_pilas,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        })
    
    @action(detail=False, methods=['get'])
    def por_pila(self, request):
        """
        Endpoint para obtener ventas de una pila específica.
        GET /api/ventas-pilas/por_pila/?pila_id=1
        """
        pila_id = request.query_params.get('pila_id')
        
        if not pila_id:
            return Response(
                {'error': 'El parámetro pila_id es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ventas = self.queryset.filter(pila_id=pila_id)
        serializer = self.get_serializer(ventas, many=True)
        
        # Calcular estadísticas
        total_vendido = sum(venta.precio_total for venta in ventas)
        cantidad_total = ventas.aggregate(total=Sum('cantidad'))['total'] or 0
        
        return Response({
            'ventas': serializer.data,
            'total_vendido': total_vendido,
            'cantidad_total_vendida': cantidad_total
        })
