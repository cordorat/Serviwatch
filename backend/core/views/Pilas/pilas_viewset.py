from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from core.models.pilas import Pilas
from core.serializers.pilas_serializer import PilasSerializer


class PilasViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el modelo Pilas.
    Proporciona operaciones CRUD completas para el inventario de pilas.
    """
    
    queryset = Pilas.objects.all().order_by('codigo')
    serializer_class = PilasSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo']
    ordering_fields = ['codigo', 'precio', 'cantidad']
    filterset_fields = ['codigo']
    
    @action(detail=False, methods=['get'])
    def bajo_stock(self, request):
        """
        Endpoint personalizado para obtener pilas con bajo stock.
        GET /api/pilas/bajo_stock/?minimo=10
        """
        minimo = int(request.query_params.get('minimo', 10))
        pilas = self.queryset.filter(cantidad__lte=str(minimo))
        serializer = self.get_serializer(pilas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def actualizar_stock(self, request, pk=None):
        """
        Endpoint para actualizar solo el stock de una pila.
        PATCH /api/pilas/{id}/actualizar_stock/
        Body: {"cantidad": "50"}
        """
        pila = self.get_object()
        nueva_cantidad = request.data.get('cantidad')
        
        if not nueva_cantidad:
            return Response(
                {'error': 'El campo cantidad es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if not nueva_cantidad.isdigit():
                return Response(
                    {'error': 'La cantidad debe ser un número válido.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            pila.cantidad = nueva_cantidad
            pila.save()
            
            serializer = self.get_serializer(pila)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
