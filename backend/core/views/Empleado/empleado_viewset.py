from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from core.models.empleado import Empleado
from core.serializers.empleado_serializer import EmpleadoSerializer


class EmpleadoPagination(PageNumberPagination):
    """
    Configuración de paginación personalizada para empleados.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class EmpleadoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar empleados a través de API REST.
    
    Endpoints generados automáticamente:
    - GET /api/empleados/ - Listar todos los empleados (con paginación)
    - POST /api/empleados/ - Crear un nuevo empleado
    - GET /api/empleados/{id}/ - Obtener un empleado específico
    - PUT /api/empleados/{id}/ - Actualizar completamente un empleado
    - PATCH /api/empleados/{id}/ - Actualizar parcialmente un empleado
    - DELETE /api/empleados/{id}/ - Eliminar un empleado
    
    Endpoints personalizados:
    - GET /api/empleados/buscar/?term=xxx - Buscar empleados
    - GET /api/empleados/activos/ - Listar solo empleados activos
    - GET /api/empleados/tecnicos/ - Listar solo técnicos
    """
    
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = EmpleadoPagination
    
    def get_queryset(self):
        """
        Personaliza el queryset para incluir búsqueda, filtrado y ordenamiento.
        """
        queryset = Empleado.objects.all()
        
        # Filtro por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtro por cargo
        cargo = self.request.query_params.get('cargo', None)
        if cargo:
            queryset = queryset.filter(cargo=cargo)
        
        # Búsqueda por término
        search_term = self.request.query_params.get('term', None)
        if search_term:
            query = Q(nombre__icontains=search_term) | \
                    Q(apellidos__icontains=search_term) | \
                    Q(cedula__icontains=search_term) | \
                    Q(celular__icontains=search_term)
            
            # Búsqueda más específica si hay múltiples términos
            terms = search_term.split()
            if len(terms) >= 2:
                # Primer término como nombre, resto como apellidos
                nombre_query = Q(nombre__icontains=terms[0])
                apellidos_query = Q(apellidos__icontains=' '.join(terms[1:]))
                query |= nombre_query & apellidos_query
                
                # Último término como apellidos, resto como nombre
                nombre_query2 = Q(nombre__icontains=' '.join(terms[:-1]))
                apellidos_query2 = Q(apellidos__icontains=terms[-1])
                query |= nombre_query2 & apellidos_query2
            
            queryset = queryset.filter(query)
        
        # Ordenamiento
        return queryset.order_by('nombre', 'apellidos')
    
    def list(self, request, *args, **kwargs):
        """
        Lista todos los empleados con paginación.
        
        Query params opcionales:
        - term: Término de búsqueda
        - estado: Filtrar por estado (Activo/Inactivo)
        - cargo: Filtrar por cargo (Técnico/Secretario/a)
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
        Crea un nuevo empleado.
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'success': True,
                'message': 'Empleado creado exitosamente.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Error al crear el empleado.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """
        Actualiza un empleado existente (PUT - requiere todos los campos).
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'success': True,
                'message': 'Empleado actualizado exitosamente.',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'message': 'Error al actualizar el empleado.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Actualiza parcialmente un empleado existente (PATCH - solo campos enviados).
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Elimina un empleado (o mejor aún, márcalo como inactivo).
        """
        instance = self.get_object()
        
        # Opción 1: Eliminar completamente (descomenta si quieres eliminar)
        # self.perform_destroy(instance)
        
        # Opción 2: Marcar como inactivo (recomendado para mantener historial)
        instance.estado = 'Inactivo'
        instance.save()
        
        return Response({
            'success': True,
            'message': 'Empleado marcado como inactivo exitosamente.'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='buscar')
    def buscar(self, request):
        """
        Endpoint personalizado para búsqueda de empleados.
        
        GET /api/empleados/buscar/?term=juan
        
        Retorna hasta 100 empleados que coincidan con el término de búsqueda.
        """
        search_term = request.query_params.get('term', '')
        
        if not search_term:
            return Response({
                'success': False,
                'message': 'Debe proporcionar un término de búsqueda.',
                'results': []
            }, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset()[:100]
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'count': len(serializer.data),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='activos')
    def activos(self, request):
        """
        Lista solo empleados activos.
        
        GET /api/empleados/activos/
        """
        queryset = Empleado.objects.filter(estado='Activo').order_by('nombre', 'apellidos')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'count': len(serializer.data),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='tecnicos')
    def tecnicos(self, request):
        """
        Lista solo empleados con cargo de Técnico.
        
        GET /api/empleados/tecnicos/
        """
        queryset = Empleado.objects.filter(
            cargo='Técnico',
            estado='Activo'
        ).order_by('nombre', 'apellidos')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'count': len(serializer.data),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['patch'], url_path='cambiar-estado')
    def cambiar_estado(self, request, pk=None):
        """
        Cambia el estado de un empleado entre Activo/Inactivo.
        
        PATCH /api/empleados/{id}/cambiar-estado/
        """
        empleado = self.get_object()
        
        # Alternar estado
        nuevo_estado = 'Inactivo' if empleado.estado == 'Activo' else 'Activo'
        empleado.estado = nuevo_estado
        empleado.save()
        
        serializer = self.get_serializer(empleado)
        return Response({
            'success': True,
            'message': f'Empleado marcado como {nuevo_estado}.',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='estadisticas')
    def estadisticas(self, request):
        """
        Retorna estadísticas de empleados.
        
        GET /api/empleados/estadisticas/
        """
        total = Empleado.objects.count()
        activos = Empleado.objects.filter(estado='Activo').count()
        inactivos = Empleado.objects.filter(estado='Inactivo').count()
        tecnicos = Empleado.objects.filter(cargo='Técnico', estado='Activo').count()
        secretarios = Empleado.objects.filter(cargo='Secretario/a', estado='Activo').count()
        
        return Response({
            'success': True,
            'estadisticas': {
                'total': total,
                'activos': activos,
                'inactivos': inactivos,
                'tecnicos': tecnicos,
                'secretarios': secretarios
            }
        })
