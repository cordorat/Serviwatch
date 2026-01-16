from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from core.models.egreso import Egreso
from core.serializers.egreso_serializer import EgresoSerializer
from datetime import date
from django.db.models import Sum


class EgresoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el modelo Egreso.
    Proporciona operaciones CRUD completas para registros de egresos financieros.
    """
    
    queryset = Egreso.objects.all().order_by('-fecha')
    serializer_class = EgresoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['descripcion']
    ordering_fields = ['fecha', 'valor']
    filterset_fields = ['fecha']
    
    @action(detail=False, methods=['get'])
    def mes_actual(self, request):
        """
        Endpoint para obtener egresos del mes actual.
        GET /api/egresos/mes_actual/
        """
        today = date.today()
        egresos = self.queryset.filter(
            fecha__year=today.year,
            fecha__month=today.month
        )
        serializer = self.get_serializer(egresos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def total_mes(self, request):
        """
        Endpoint para obtener el total de egresos del mes actual.
        GET /api/egresos/total_mes/
        """
        today = date.today()
        total = self.queryset.filter(
            fecha__year=today.year,
            fecha__month=today.month
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        return Response({'total': total, 'mes': today.month, 'anio': today.year})
    
    @action(detail=False, methods=['get'])
    def por_rango(self, request):
        """
        Endpoint para obtener egresos por rango de fechas.
        GET /api/egresos/por_rango/?fecha_inicio=2024-01-01&fecha_fin=2024-12-31
        """
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return Response(
                {'error': 'Se requieren fecha_inicio y fecha_fin.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        egresos = self.queryset.filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin
        )
        
        total = egresos.aggregate(total=Sum('valor'))['total'] or 0
        serializer = self.get_serializer(egresos, many=True)
        
        return Response({
            'egresos': serializer.data,
            'total': total,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        })
