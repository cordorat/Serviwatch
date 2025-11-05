from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from core.models import Cliente
from core.serializers.cliente_serializer import ClienteSerializer


class ClientePagination(PageNumberPagination):
    """
    Configuración de paginación personalizada para clientes.
    """
    page_size = 10  # Cambia este número al que necesites
    page_size_query_param = 'page_size'  # Permite ?page_size=X en la URL
    max_page_size = 100  # Máximo permitido por seguridad


class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar clientes a través de API REST.
    
    Endpoints generados automáticamente:
    - GET /api/clientes/ - Listar todos los clientes (con paginación)
    - POST /api/clientes/ - Crear un nuevo cliente
    - GET /api/clientes/{id}/ - Obtener un cliente específico
    - PUT /api/clientes/{id}/ - Actualizar completamente un cliente
    - PATCH /api/clientes/{id}/ - Actualizar parcialmente un cliente
    - DELETE /api/clientes/{id}/ - Eliminar un cliente
    
    Endpoints personalizados:
    - GET /api/clientes/buscar/?term=xxx - Buscar clientes por nombre, apellido o teléfono
    """
    
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ClientePagination
    
    def get_queryset(self):
        """
        Personaliza el queryset para incluir búsqueda y ordenamiento.
        """
        queryset = Cliente.objects.all()
        
        # Búsqueda por término
        search_term = self.request.query_params.get('term', None)
        if search_term:
            # Búsqueda básica por nombre, apellido o teléfono
            query = Q(nombre__icontains=search_term) | \
                    Q(apellido__icontains=search_term) | \
                    Q(telefono__icontains=search_term)
            
            # Búsqueda más específica si hay múltiples términos
            terms = search_term.split()
            if len(terms) >= 2:
                # Primer término como nombre, resto como apellido
                nombre_query = Q(nombre__icontains=terms[0])
                apellido_query = Q(apellido__icontains=' '.join(terms[1:]))
                query |= nombre_query & apellido_query
                
                # Último término como apellido, resto como nombre
                nombre_query2 = Q(nombre__icontains=' '.join(terms[:-1]))
                apellido_query2 = Q(apellido__icontains=terms[-1])
                query |= nombre_query2 & apellido_query2
            
            queryset = queryset.filter(query)
        
        # Ordenamiento
        return queryset.order_by('nombre', 'apellido', 'telefono')
    
    def list(self, request, *args, **kwargs):
        """
        Lista todos los clientes con paginación.
        
        Query params opcionales:
        - term: Término de búsqueda
        - page: Número de página
        - page_size: Tamaño de página (máx. 100)
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Contar resultados antes de paginar
        total_count = queryset.count()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['total_count'] = total_count
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'count': total_count,
            'total_count': total_count
        })
    
    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo cliente.
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'success': True,
                'message': 'Cliente creado exitosamente.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Error al crear el cliente.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """
        Actualiza un cliente existente (PUT - requiere todos los campos).
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'success': True,
                'message': 'Cliente actualizado exitosamente.',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'message': 'Error al actualizar el cliente.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Actualiza parcialmente un cliente existente (PATCH - solo campos enviados).
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Elimina un cliente.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'Cliente eliminado exitosamente.'
        }, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'], url_path='buscar')
    def buscar(self, request):
        """
        Endpoint personalizado para búsqueda de clientes.
        
        GET /api/clientes/buscar/?term=juan
        
        Retorna hasta 100 clientes que coincidan con el término de búsqueda.
        Útil para autocompletado.
        """
        search_term = request.query_params.get('term', '')
        
        if not search_term:
            return Response({
                'success': False,
                'message': 'Debe proporcionar un término de búsqueda.',
                'results': []
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Reutilizar la lógica de búsqueda del get_queryset
        queryset = self.get_queryset()[:100]  # Limitar a 100 resultados
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'count': len(serializer.data),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='autocompletado')
    def autocompletado(self, request):
        """
        Endpoint para autocompletado.
        
        GET /api/clientes/autocompletado/?term=juan
        
        Retorna solo id, nombre_completo y teléfono para optimizar la respuesta.
        """
        search_term = request.query_params.get('term', '')
        
        queryset = Cliente.objects.all()
        
        if search_term:
            query = Q(nombre__icontains=search_term) | \
                    Q(apellido__icontains=search_term) | \
                    Q(telefono__icontains=search_term)
            queryset = queryset.filter(query)
        
        queryset = queryset.order_by('nombre', 'apellido')[:100]
        
        # Serialización ligera solo con campos necesarios
        results = [
            {
                'id': cliente.id,
                'nombre_completo': f"{cliente.nombre} {cliente.apellido}",
                'telefono': cliente.telefono
            }
            for cliente in queryset
        ]
        
        return Response({
            'success': True,
            'count': len(results),
            'results': results
        })
