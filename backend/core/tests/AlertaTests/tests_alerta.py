from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date
from core.models.reparacion import Reparacion
from core.models.pilas import Pilas
from core.models.cliente import Cliente
from core.models.empleado import Empleado


class AlertaViewTestCase(TestCase):
    """Test cases para la vista de alertas"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = Client()
        
        # Crear usuario para las pruebas
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Crear cliente de prueba
        self.cliente = Cliente.objects.create(
            nombre='Juan',
            apellido='Pérez',
            telefono='1234567890'
        )
        
        # Crear empleado de prueba
        self.empleado = Empleado.objects.create(
            cedula='1234567890',
            nombre='Carlos',
            apellidos='González',
            fecha_ingreso=timezone.now().date(),
            fecha_nacimiento=date(1990, 1, 1)
        )
        
        # Fecha actual para los tests
        self.fecha_actual = timezone.now().date()
        
    def test_alerta_view_requires_login(self):
        """Test que verifica que la vista requiere autenticación"""
        url = reverse('alertas')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirección al login
        
    def test_alerta_view_proxima_entrega_default(self):
        """Test para verificar que por defecto muestra próximas entregas"""
        self.client.login(username='testuser', password='testpass123')
        
        # Crear reparación que vence en 5 días
        fecha_entrega = self.fecha_actual + timedelta(days=5)
        reparacion = Reparacion.objects.create(
            cliente=self.cliente,
            marca_reloj='Rolex',
            descripcion='Reparación de prueba',
            codigo_orden='TEST001',
            fecha_entrega_estimada=fecha_entrega,
            precio=100000,
            espacio_fisico='A1',
            estado='Reparación',
            tecnico=self.empleado
        )
        
        url = reverse('alertas')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['tipo_actual'], 'proxima_entrega')
        self.assertIn(reparacion, response.context['items'])
        self.assertEqual(response.context['contador_entregas'], 1)
        
    def test_alerta_view_proxima_entrega_filtro(self):
        """Test para filtrar reparaciones por próxima entrega"""
        self.client.login(username='testuser', password='testpass123')
        
        # Crear reparaciones con diferentes fechas de entrega
        # Reparación que vence en 3 días (debe aparecer)
        reparacion_pronta = Reparacion.objects.create(
            cliente=self.cliente,
            marca_reloj='Casio',
            descripcion='Reparación pronta',
            codigo_orden='TEST002',
            fecha_entrega_estimada=self.fecha_actual + timedelta(days=3),
            precio=50000,
            espacio_fisico='B1',
            estado='Listo',
            tecnico=self.empleado
        )
        
        # Reparación que vence en 10 días (no debe aparecer)
        reparacion_lejana = Reparacion.objects.create(
            cliente=self.cliente,
            marca_reloj='Seiko',
            descripcion='Reparación lejana',
            codigo_orden='TEST003',
            fecha_entrega_estimada=self.fecha_actual + timedelta(days=10),
            precio=75000,
            espacio_fisico='C1',
            estado='Cotización',
            tecnico=self.empleado
        )
        
        # Reparación ya entregada (no debe aparecer)
        reparacion_entregada = Reparacion.objects.create(
            cliente=self.cliente,
            marca_reloj='Omega',
            descripcion='Reparación entregada',
            codigo_orden='TEST004',
            fecha_entrega_estimada=self.fecha_actual + timedelta(days=2),
            precio=200000,
            espacio_fisico='D1',
            estado='Entregado',
            tecnico=self.empleado
        )
        
        url = reverse('alertas')
        response = self.client.get(url, {'tipo': 'proxima_entrega'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(reparacion_pronta, response.context['items'])
        self.assertNotIn(reparacion_lejana, response.context['items'])
        self.assertNotIn(reparacion_entregada, response.context['items'])
        
    def test_alerta_view_stock_bajo(self):
        """Test para filtrar pilas con stock bajo"""
        self.client.login(username='testuser', password='testpass123')
        
        # Crear pilas con diferentes cantidades
        pila_stock_bajo = Pilas.objects.create(
            codigo='PILA001',
            precio='15000',
            cantidad='3'  # Stock bajo
        )
        
        pila_stock_normal = Pilas.objects.create(
            codigo='PILA002',
            precio='20000',
            cantidad='10'  # Stock normal
        )
        
        url = reverse('alertas')
        response = self.client.get(url, {'tipo': 'stock_bajo'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['tipo_actual'], 'stock_bajo')
        self.assertIn(pila_stock_bajo, response.context['items'])
        self.assertNotIn(pila_stock_normal, response.context['items'])
        self.assertEqual(response.context['contador_stock'], 1)
        
    def test_alerta_view_proxima_revision(self):
        """Test para filtrar reparaciones que necesitan revisión"""
        self.client.login(username='testuser', password='testpass123')
        
        # Crear reparación de mantenimiento entregada hace más de 3 años
        fecha_ingreso_antigua = self.fecha_actual - timedelta(days=365*4)  # Hace 4 años
        reparacion_revision = Reparacion.objects.create(
            cliente=self.cliente,
            marca_reloj='TAG Heuer',
            descripcion='Mantenimiento antiguo',
            codigo_orden='TEST005',
            fecha_entrega_estimada=self.fecha_actual,
            precio=300000,
            espacio_fisico='E1',
            estado='Entregado',
            tecnico=self.empleado,
            mantenimiento=True
        )
        # Establecer fecha de ingreso manualmente
        reparacion_revision.fecha_ingreso = fecha_ingreso_antigua
        reparacion_revision.save()
        
        # Crear reparación reciente que no necesita revisión
        reparacion_reciente = Reparacion.objects.create(
            cliente=self.cliente,
            marca_reloj='Citizen',
            descripcion='Mantenimiento reciente',
            codigo_orden='TEST006',
            fecha_entrega_estimada=self.fecha_actual,
            precio=150000,
            espacio_fisico='F1',
            estado='Entregado',
            tecnico=self.empleado,
            mantenimiento=True
        )
        
        url = reverse('alertas')
        response = self.client.get(url, {'tipo': 'proxima_revision'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['tipo_actual'], 'proxima_revision')
        self.assertIn(reparacion_revision, response.context['items'])
        self.assertNotIn(reparacion_reciente, response.context['items'])
        
    def test_alerta_view_contadores_correctos(self):
        """Test para verificar que los contadores se calculan correctamente"""
        self.client.login(username='testuser', password='testpass123')
        
        # Crear datos para cada tipo de alerta
        
        # 2 reparaciones próximas a entregar
        for i in range(2):
            Reparacion.objects.create(
                cliente=self.cliente,
                marca_reloj=f'Marca{i}',
                descripcion=f'Descripción {i}',
                codigo_orden=f'TEST00{i+7}',
                fecha_entrega_estimada=self.fecha_actual + timedelta(days=5),
                precio=100000,
                espacio_fisico=f'G{i+1}',
                estado='Reparación',
                tecnico=self.empleado
            )
        
        # 3 pilas con stock bajo
        for i in range(3):
            Pilas.objects.create(
                codigo=f'PILA00{i+3}',
                precio='12000',
                cantidad='2'
            )
        
        # 1 reparación que necesita revisión
        fecha_ingreso_antigua = self.fecha_actual - timedelta(days=365*4)
        reparacion_revision = Reparacion.objects.create(
            cliente=self.cliente,
            marca_reloj='Longines',
            descripcion='Necesita revisión',
            codigo_orden='TEST009',
            fecha_entrega_estimada=self.fecha_actual,
            precio=250000,
            espacio_fisico='H1',
            estado='Entregado',
            tecnico=self.empleado,
            mantenimiento=True
        )
        reparacion_revision.fecha_ingreso = fecha_ingreso_antigua
        reparacion_revision.save()
        
        url = reverse('alertas')
        response = self.client.get(url)
        
        self.assertEqual(response.context['contador_entregas'], 2)
        self.assertEqual(response.context['contador_stock'], 3)
        self.assertEqual(response.context['contador_revision'], 1)
        self.assertEqual(response.context['total_alertas'], 6)
        
    def test_alerta_view_paginacion(self):
        """Test para verificar que la paginación funciona correctamente"""
        self.client.login(username='testuser', password='testpass123')
        
        # Crear más de 6 reparaciones para probar la paginación
        for i in range(8):
            Reparacion.objects.create(
                cliente=self.cliente,
                marca_reloj=f'Marca{i}',
                descripcion=f'Descripción {i}',
                codigo_orden=f'PAGE{i:03d}',
                fecha_entrega_estimada=self.fecha_actual + timedelta(days=3),
                precio=100000,
                espacio_fisico=f'P{i+1}',
                estado='Listo',
                tecnico=self.empleado
            )
        
        url = reverse('alertas')
        
        # Primera página
        response = self.client.get(url, {'tipo': 'proxima_entrega'})
        self.assertEqual(len(response.context['items']), 6)
        self.assertTrue(response.context['page_obj'].has_next())
        
        # Segunda página
        response = self.client.get(url, {'tipo': 'proxima_entrega', 'page': 2})
        self.assertEqual(len(response.context['items']), 2)
        self.assertFalse(response.context['page_obj'].has_next())
        
    def test_alerta_view_estados_excluidos(self):
        """Test para verificar que no se incluyen reparaciones entregadas en próximas entregas"""
        self.client.login(username='testuser', password='testpass123')
        
        # Crear reparación entregada
        reparacion_entregada = Reparacion.objects.create(
            cliente=self.cliente,
            marca_reloj='Excluida',
            descripcion='Esta no debe aparecer',
            codigo_orden='EXCL001',
            fecha_entrega_estimada=self.fecha_actual + timedelta(days=2),
            precio=100000,
            espacio_fisico='EX1',
            estado='Entregado',
            tecnico=self.empleado
        )
        
        url = reverse('alertas')
        response = self.client.get(url, {'tipo': 'proxima_entrega'})
        
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(reparacion_entregada, response.context['items'])
        
    def test_alerta_view_orden_correcto(self):
        """Test para verificar el orden correcto de los elementos"""
        self.client.login(username='testuser', password='testpass123')
        
        # Crear reparaciones con diferentes fechas de entrega
        reparacion1 = Reparacion.objects.create(
            cliente=self.cliente,
            marca_reloj='Primera',
            descripcion='Vence primero',
            codigo_orden='ORD001',
            fecha_entrega_estimada=self.fecha_actual + timedelta(days=2),
            precio=100000,
            espacio_fisico='O1',
            estado='Listo',
            tecnico=self.empleado
        )
        
        reparacion2 = Reparacion.objects.create(
            cliente=self.cliente,
            marca_reloj='Segunda',
            descripcion='Vence después',
            codigo_orden='ORD002',
            fecha_entrega_estimada=self.fecha_actual + timedelta(days=5),
            precio=100000,
            espacio_fisico='O2',
            estado='Listo',
            tecnico=self.empleado
        )
        
        url = reverse('alertas')
        response = self.client.get(url, {'tipo': 'proxima_entrega'})
        
        items_list = list(response.context['items'])
        self.assertEqual(items_list[0], reparacion1)
        self.assertEqual(items_list[1], reparacion2)
        
    def test_alerta_view_pilas_orden_cantidad(self):
        """Test para verificar que las pilas se ordenan por cantidad"""
        self.client.login(username='testuser', password='testpass123')
        
        pila1 = Pilas.objects.create(
            codigo='PILA_MENOS',
            precio='15000',
            cantidad='1'  # Menor cantidad
        )
        
        pila2 = Pilas.objects.create(
            codigo='PILA_MAS',
            precio='15000',
            cantidad='4'  # Mayor cantidad pero aún stock bajo
        )
        
        url = reverse('alertas')
        response = self.client.get(url, {'tipo': 'stock_bajo'})
        
        items_list = list(response.context['items'])
        self.assertEqual(items_list[0], pila1)  # Menor cantidad primero
        self.assertEqual(items_list[1], pila2)
        
    def test_alerta_view_template_utilizado(self):
        """Test para verificar que se utiliza el template correcto"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('alertas')
        response = self.client.get(url)
        
        self.assertTemplateUsed(response, 'alerta/alerta_list.html')
        
    def test_alerta_view_metodo_get_only(self):
        """Test para verificar que solo acepta método GET"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('alertas')
        
        # GET debe funcionar
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # POST debe ser rechazado
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
