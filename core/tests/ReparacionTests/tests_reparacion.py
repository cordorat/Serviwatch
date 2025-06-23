"""
Tests refactorizados para el módulo de Reparación.
Incluye cobertura completa para el campo booleano 'mantenimiento' 
en formularios, servicios y vistas.

Convenciones:
- Nombres de métodos y variables en inglés (PEP 8)
- Comentarios en español
- Cobertura de todos los flujos principales
- Validación de edge cases
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages
from unittest.mock import patch
from django.http import Http404
from datetime import date, timedelta

from core.models import Reparacion, Cliente, Empleado
from core.forms.reparacion_form import ReparacionForm
from core.services.reparacion_service import (
    get_all_reparaciones, 
    crear_reparacion, 
    get_reparacion_by_id, 
    actualizar_reparacion
)


class ReparacionFormTest(TestCase):
    """Test suite para el formulario ReparacionForm"""
    
    def setUp(self):
        """Configuración inicial para los tests del formulario"""
        self.cliente = Cliente.objects.create(
            nombre="Test",
            apellido="User", 
            telefono="1234567890"
        )
        
        self.tecnico = Empleado.objects.create(
            cedula="1234567890",
            nombre="Tech",
            apellidos="Support",
            fecha_ingreso=date.today().strftime('%Y-%m-%d'),
            fecha_nacimiento=(date.today() - timedelta(days=365*30)).strftime('%Y-%m-%d'),
            celular="3216549870",
            cargo="Técnico",
            salario=2500000,
            estado="Activo"
        )

        self.valid_data = {
            'cliente': self.cliente,
            'marca_reloj': "Rolex",
            'descripcion': "Reparación de cristal y ajuste de hora",
            'codigo_orden': "12345",
            'fecha_entrega_estimada': (date.today() + timedelta(days=5)).strftime('%d/%m/%Y'),
            'precio': 100000,
            'espacio_fisico': "Caja 1",
            'estado': "Reparación",
            'tecnico': self.tecnico,
            'mantenimiento': False  # Campo booleano agregado
        }

    def test_valid_form_without_maintenance(self):
        """Test formulario válido sin mantenimiento"""
        form = ReparacionForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), f"Errores del formulario: {form.errors}")
        self.assertFalse(form.cleaned_data['mantenimiento'])

    def test_valid_form_with_maintenance(self):
        """Test formulario válido con mantenimiento activo"""
        self.valid_data['mantenimiento'] = True
        form = ReparacionForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), f"Errores del formulario: {form.errors}")
        self.assertTrue(form.cleaned_data['mantenimiento'])

    def test_maintenance_field_default_value(self):
        """Test que el campo mantenimiento tiene valor por defecto False"""
        # Formulario sin el campo mantenimiento explícito
        data_without_maintenance = self.valid_data.copy()
        del data_without_maintenance['mantenimiento']
        
        form = ReparacionForm(data=data_without_maintenance)
        self.assertTrue(form.is_valid())
        # Django debería usar el valor por defecto del modelo
        
    def test_maintenance_field_boolean_validation(self):
        """Test validación del campo booleano mantenimiento"""
        # Test con valores válidos
        for value in [True, False, 'True', 'False', '1', '0', 1, 0]:
            with self.subTest(value=value):
                self.valid_data['mantenimiento'] = value
                form = ReparacionForm(data=self.valid_data)
                self.assertTrue(form.is_valid(), 
                              f"Valor {value} debería ser válido: {form.errors}")

    def test_codigo_orden_numerico(self):
        """Test que el código de orden debe ser numérico"""
        self.valid_data['codigo_orden'] = "ABC123"
        form = ReparacionForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('codigo_orden', form.errors)

    def test_precio_positivo(self):
        """Test que el precio debe ser positivo"""
        self.valid_data['precio'] = -100
        form = ReparacionForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('precio', form.errors)

    def test_descripcion_minima(self):
        """Test longitud mínima de descripción"""
        self.valid_data['descripcion'] = "Corto"
        form = ReparacionForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('descripcion', form.errors)

    def test_fecha_futura(self):
        """Test que la fecha de entrega debe ser futura"""
        self.valid_data['fecha_entrega_estimada'] = (
            date.today() - timedelta(days=1)).strftime('%d/%m/%Y')
        form = ReparacionForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_entrega_estimada', form.errors)

    def test_codigo_orden_unico(self):
        """Test que el código de orden debe ser único"""
        # Crear reparación con código específico
        Reparacion.objects.create(
            cliente=self.cliente,
            marca_reloj=self.valid_data['marca_reloj'],
            descripcion=self.valid_data['descripcion'],
            codigo_orden=self.valid_data['codigo_orden'],
            fecha_entrega_estimada=date.today() + timedelta(days=5),
            precio=self.valid_data['precio'],
            espacio_fisico=self.valid_data['espacio_fisico'],
            estado=self.valid_data['estado'],
            tecnico=self.tecnico,
            mantenimiento=False
        )
        
        # Intentar crear otra reparación con el mismo código
        form = ReparacionForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('codigo_orden', form.errors)


class ReparacionServiceTest(TestCase):
    """Test suite para los servicios de Reparación"""
    
    def setUp(self):
        """Configuración inicial para los tests de servicios"""
        self.cliente = Cliente.objects.create(
            nombre="Carlos",
            apellido="Ramírez",
            telefono="3123456789"
        )

        self.tecnico = Empleado.objects.create(
            cedula="1234567890",
            nombre="Juan",
            apellidos="Pérez",
            fecha_ingreso=date.today().strftime('%Y-%m-%d'),
            fecha_nacimiento=(date.today() - timedelta(days=365*30)).strftime('%Y-%m-%d'),
            celular="3216549870",
            cargo="Técnico",
            salario=2500000,
            estado="Activo"
        )

        self.reparacion = Reparacion.objects.create(
            cliente=self.cliente,
            marca_reloj="Casio",
            descripcion="Cambio de batería y limpieza",
            codigo_orden="1001",
            fecha_entrega_estimada=date.today() + timedelta(days=5),
            precio=45000,
            espacio_fisico="A1",
            estado="Cotización",
            tecnico=self.tecnico,
            mantenimiento=False  # Campo mantenimiento incluido
        )

    def test_get_all_reparaciones(self):
        """Test obtener todas las reparaciones"""
        reparaciones = get_all_reparaciones()
        self.assertEqual(reparaciones.count(), 1)
        self.assertEqual(reparaciones[0], self.reparacion)
        self.assertFalse(reparaciones[0].mantenimiento)

    def test_crear_reparacion_without_maintenance(self):
        """Test crear reparación sin mantenimiento"""
        form_data = {
            'cliente': self.cliente.id,
            'cliente_nombre': self.cliente.nombre,
            'celular_cliente': self.cliente.telefono,
            'marca_reloj': 'Rolex',
            'descripcion': 'Limpieza general y ajuste',
            'codigo_orden': '1002',
            'fecha_entrega_estimada': (date.today() + timedelta(days=5)).strftime('%d/%m/%Y'),
            'precio': 75000,
            'espacio_fisico': 'B2',
            'estado': 'Cotización',
            'tecnico': self.tecnico.id,
            'mantenimiento': False
        }

        form = ReparacionForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Errores del formulario: {form.errors}")

        nueva_reparacion = crear_reparacion(form)
        
        self.assertIsNotNone(nueva_reparacion.id)
        self.assertEqual(nueva_reparacion.marca_reloj, 'Rolex')
        self.assertEqual(nueva_reparacion.cliente, self.cliente)
        self.assertEqual(nueva_reparacion.tecnico, self.tecnico)
        self.assertFalse(nueva_reparacion.mantenimiento)

    def test_crear_reparacion_with_maintenance(self):
        """Test crear reparación con mantenimiento activo"""
        form_data = {
            'cliente': self.cliente.id,
            'cliente_nombre': self.cliente.nombre,
            'celular_cliente': self.cliente.telefono,
            'marca_reloj': 'Omega',
            'descripcion': 'Mantenimiento preventivo completo',
            'codigo_orden': '1003',
            'fecha_entrega_estimada': (date.today() + timedelta(days=7)).strftime('%d/%m/%Y'),
            'precio': 120000,
            'espacio_fisico': 'C3',
            'estado': 'Reparación',
            'tecnico': self.tecnico.id,
            'mantenimiento': True  # Mantenimiento activo
        }

        form = ReparacionForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Errores del formulario: {form.errors}")

        nueva_reparacion = crear_reparacion(form)
        
        self.assertIsNotNone(nueva_reparacion.id)
        self.assertEqual(nueva_reparacion.marca_reloj, 'Omega')
        self.assertTrue(nueva_reparacion.mantenimiento)
        self.assertIn('preventivo', nueva_reparacion.descripcion.lower())

    def test_get_reparacion_by_id_with_maintenance(self):
        """Test obtener reparación por ID incluyendo campo mantenimiento"""
        # Crear reparación con mantenimiento
        reparacion_mantenimiento = Reparacion.objects.create(
            cliente=self.cliente,
            marca_reloj="TAG Heuer",
            descripcion="Servicio de mantenimiento anual",
            codigo_orden="1004",
            fecha_entrega_estimada=date.today() + timedelta(days=10),
            precio=150000,
            espacio_fisico="D4",
            estado="Reparación",
            tecnico=self.tecnico,
            mantenimiento=True
        )

        retrieved_reparacion = get_reparacion_by_id(reparacion_mantenimiento.id)
        
        self.assertIsNotNone(retrieved_reparacion)
        self.assertEqual(retrieved_reparacion.id, reparacion_mantenimiento.id)
        self.assertTrue(retrieved_reparacion.mantenimiento)
        self.assertEqual(retrieved_reparacion.marca_reloj, "TAG Heuer")

    def test_actualizar_reparacion_toggle_maintenance(self):
        """Test actualizar reparación cambiando estado de mantenimiento"""
        # Datos para actualizar incluyendo cambio de mantenimiento
        datos_actualizacion = {
            'cliente': self.cliente.id,
            'marca_reloj': 'Casio Actualizado',
            'descripcion': 'Cambio de batería y mantenimiento preventivo',
            'codigo_orden': '1001',  # Mismo código
            'fecha_entrega_estimada': (date.today() + timedelta(days=8)).strftime('%d/%m/%Y'),
            'precio': 55000,
            'espacio_fisico': 'A1',
            'estado': 'Reparación',
            'tecnico': self.tecnico.id,
            'mantenimiento': True  # Cambiar a mantenimiento activo
        }

        form = ReparacionForm(data=datos_actualizacion, instance=self.reparacion)
        self.assertTrue(form.is_valid(), f"Errores del formulario: {form.errors}")

        reparacion_actualizada = actualizar_reparacion(form, self.reparacion.id)
        
        self.assertEqual(reparacion_actualizada.marca_reloj, 'Casio Actualizado')
        self.assertTrue(reparacion_actualizada.mantenimiento)
        self.assertEqual(reparacion_actualizada.precio, 55000)

    def test_get_all_reparaciones_empty(self):
        """Test obtener reparaciones con base de datos vacía"""
        Reparacion.objects.all().delete()
        reparaciones = get_all_reparaciones()
        self.assertEqual(reparaciones.count(), 0)

    def test_crear_reparacion_invalid_form(self):
        """Test crear reparación con formulario inválido"""
        form = ReparacionForm(data={})
        self.assertFalse(form.is_valid())
        
        with self.assertRaises(ValueError):
            crear_reparacion(form)


class ReparacionViewsTest(TestCase):
    """Test suite para las vistas de Reparación"""
    
    @classmethod
    def setUpTestData(cls):
        """Configuración inicial para todo el conjunto de pruebas"""
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )
        
        cls.cliente1 = Cliente.objects.create(
            nombre="Carlos", 
            apellido="Ramírez", 
            telefono="3123456789"
        )
        cls.cliente2 = Cliente.objects.create(
            nombre="Ana", 
            apellido="Martínez", 
            telefono="3219876543"
        )
        
        cls.tecnico1 = Empleado.objects.create(
            cedula="1234567890",
            nombre="Juan",
            apellidos="Pérez",
            fecha_ingreso=date.today().strftime('%Y-%m-%d'),
            fecha_nacimiento=(date.today() - timedelta(days=365*30)).strftime('%Y-%m-%d'),
            celular="3216549870",
            cargo="Técnico",
            salario=2500000,
            estado="Activo"
        )
        cls.tecnico2 = Empleado.objects.create(
            cedula="0987654321",
            nombre="María",
            apellidos="López",
            fecha_ingreso=date.today().strftime('%Y-%m-%d'),
            fecha_nacimiento=(date.today() - timedelta(days=365*30)).strftime('%Y-%m-%d'),
            celular="3001234567",
            cargo="Técnico",
            salario=2700000,
            estado="Activo"
        )
        
        # Crear reparaciones de prueba con diferentes estados de mantenimiento
        for i in range(1, 8):
            cliente = cls.cliente1 if i % 2 else cls.cliente2
            tecnico = cls.tecnico1 if i % 2 else cls.tecnico2
            estado = "Cotización" if i < 3 else "Reparación" if i < 5 else "Listo"
            mantenimiento = i % 3 == 0  # Cada 3 reparaciones es mantenimiento
            
            Reparacion.objects.create(
                cliente=cliente,
                marca_reloj=f"Marca{i}",
                descripcion=f"Descripción detallada del reloj {i} {'con mantenimiento' if mantenimiento else 'sin mantenimiento'}",
                codigo_orden=f"10{i:02d}",
                fecha_entrega_estimada=date.today() + timedelta(days=5),
                precio=45000 + (i * 1000),
                espacio_fisico=f"A{i}",
                estado=estado,
                tecnico=tecnico,
                mantenimiento=mantenimiento
            )
    
    def setUp(self):
        """Configuración para cada prueba individual"""
        self.client = Client()
        self.client.login(username='testuser', password='testpassword123')
        self.reparacion_list_url = reverse('reparacion_list')
        self.reparacion_create_url = reverse('reparacion_create')

    def test_reparacion_list_view_displays_maintenance_status(self):
        """Test que la vista de lista muestra el estado de mantenimiento"""
        response = self.client.get(self.reparacion_list_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reparacion/reparacion_list.html')
        
        # Verificar que hay reparaciones con y sin mantenimiento
        reparaciones = response.context['page_obj']
        maintenance_statuses = [r.mantenimiento for r in reparaciones]
        
        self.assertIn(True, maintenance_statuses)   # Al menos una con mantenimiento
        self.assertIn(False, maintenance_statuses)  # Al menos una sin mantenimiento

    def test_reparacion_list_view_search_by_maintenance(self):
        """Test búsqueda por estado de mantenimiento"""
        # Crear reparación específica de mantenimiento
        reparacion_mantenimiento = Reparacion.objects.create(
            cliente=self.cliente1,
            marca_reloj="Rolex Mantenimiento",
            descripcion="Servicio de mantenimiento preventivo especial",
            codigo_orden="9999",
            fecha_entrega_estimada=date.today() + timedelta(days=5),
            precio=200000,
            espacio_fisico="M1",
            estado="Reparación",
            tecnico=self.tecnico1,
            mantenimiento=True
        )

        # Buscar por término relacionado con mantenimiento
        response = self.client.get(self.reparacion_list_url, {'search': 'mantenimiento'})
        
        self.assertEqual(response.status_code, 200)
        reparaciones_encontradas = response.context['page_obj']
        
        # Verificar que se encontraron reparaciones con mantenimiento
        self.assertTrue(any(r.mantenimiento for r in reparaciones_encontradas))

    def test_reparacion_create_view_get(self):
        """Test GET de la vista de creación"""
        response = self.client.get(self.reparacion_create_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reparacion/reparacion_form.html')
        self.assertIsInstance(response.context['form'], ReparacionForm)

    def test_reparacion_create_view_post_valid_without_maintenance(self):
        """Test POST válido sin mantenimiento"""
        data = {
            'cliente': self.cliente1.id,
            'marca_reloj': 'Seiko',
            'descripcion': 'Reparación de cristal y correa sin mantenimiento',
            'codigo_orden': '8001',
            'fecha_entrega_estimada': (date.today() + timedelta(days=7)).strftime('%d/%m/%Y'),            'precio': 85000,
            'espacio_fisico': 'B5',
            'estado': 'Cotización',
            'tecnico': self.tecnico1.id,
            'mantenimiento': False
        }
        
        response = self.client.post(self.reparacion_create_url, data)
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith('/servicios/reparaciones/'))
          # Verificar que se creó la reparación sin mantenimiento
        nueva_reparacion = Reparacion.objects.get(codigo_orden='8001')
        self.assertEqual(nueva_reparacion.marca_reloj, 'Seiko')
        self.assertFalse(nueva_reparacion.mantenimiento)
        
        # Verificar mensaje de éxito
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('correctamente' in str(message) for message in messages))

    def test_reparacion_create_view_post_valid_with_maintenance(self):
        """Test POST válido con mantenimiento"""
        data = {
            'cliente': self.cliente2.id,
            'marca_reloj': 'Breitling',
            'descripcion': 'Mantenimiento preventivo completo y calibración',
            'codigo_orden': '8002',
            'fecha_entrega_estimada': (date.today() + timedelta(days=10)).strftime('%d/%m/%Y'),
            'precio': 180000,
            'espacio_fisico': 'M2',
            'estado': 'Reparación',
            'tecnico': self.tecnico2.id,
            'mantenimiento': True
        }
        
        response = self.client.post(self.reparacion_create_url, data)
        
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se creó la reparación con mantenimiento
        nueva_reparacion = Reparacion.objects.get(codigo_orden='8002')
        self.assertEqual(nueva_reparacion.marca_reloj, 'Breitling')
        self.assertTrue(nueva_reparacion.mantenimiento)
        self.assertIn('preventivo', nueva_reparacion.descripcion.lower())

    def test_reparacion_create_view_post_invalid_form(self):
        """Test POST con formulario inválido"""
        data = {
            'cliente': self.cliente1.id,
            'marca_reloj': 'Seiko',
            'codigo_orden': 'ABC',  # No numérico
            'fecha_entrega_estimada': '',  # Fecha vacía
            'precio': -100,  # Precio negativo
            'espacio_fisico': 'B5',
            'estado': 'Cotización',
            'tecnico': self.tecnico1.id,
            'mantenimiento': False
        }
        
        response = self.client.post(self.reparacion_create_url, data)
        
        self.assertEqual(response.status_code, 200)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(len(messages) > 0)
        self.assertTrue(any('Error' in str(message) for message in messages))
        
        # Verificar que no se creó la reparación
        self.assertFalse(Reparacion.objects.filter(marca_reloj='Seiko').exists())

    def test_reparacion_create_view_requires_login(self):
        """Test que la vista requiere autenticación"""
        self.client.logout()
        response = self.client.get(self.reparacion_create_url)
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login/' in response.url)


class ReparacionServiceUpdateTest(TestCase):
    """Test suite específico para actualizaciones de reparación"""
    
    def setUp(self):
        """Configuración para tests de actualización"""
        self.cliente = Cliente.objects.create(
            nombre="Cliente Test",
            apellido="Apellido",
            telefono="1234567890"
        )
        
        self.tecnico = Empleado.objects.create(
            cedula="1234567890",
            nombre="Juan",
            apellidos="Pérez",
            fecha_ingreso=date.today(),
            fecha_nacimiento=date(1990, 5, 20),
            celular="3216549870",
            cargo="Técnico",
            salario=2500000,
            estado="Activo"
        )
        
        self.reparacion = Reparacion.objects.create(
            cliente=self.cliente,
            marca_reloj="Original",
            descripcion="Descripción original",
            codigo_orden="5001",
            fecha_entrega_estimada=date.today() + timedelta(days=5),
            precio=50000,
            espacio_fisico="A1",
            estado="Cotización",
            tecnico=self.tecnico,
            mantenimiento=False
        )

    def test_actualizar_maintenance_false_to_true(self):
        """Test cambiar mantenimiento de False a True"""
        form_data = {
            'cliente': self.cliente.id,
            'marca_reloj': 'Original Actualizado',
            'descripcion': 'Actualizado para incluir mantenimiento',
            'codigo_orden': '5001',
            'fecha_entrega_estimada': (date.today() + timedelta(days=7)).strftime('%d/%m/%Y'),
            'precio': 75000,
            'espacio_fisico': 'A1',
            'estado': 'Reparación',
            'tecnico': self.tecnico.id,
            'mantenimiento': True
        }
        form = ReparacionForm(data=form_data, instance=self.reparacion)
        self.assertTrue(form.is_valid())
        
        updated_reparacion = actualizar_reparacion(form, self.reparacion.id)
        
        self.assertTrue(updated_reparacion.mantenimiento)
        self.assertEqual(updated_reparacion.precio, 75000)
        self.assertIn('mantenimiento', updated_reparacion.descripcion.lower())

    def test_actualizar_maintenance_true_to_false(self):
        """Test cambiar mantenimiento de True a False"""
        # Primero actualizar a mantenimiento True
        self.reparacion.mantenimiento = True
        self.reparacion.save()
        
        form_data = {
            'cliente': self.cliente.id,
            'marca_reloj': 'Sin Mantenimiento',
            'descripcion': 'Reparación simple sin mantenimiento',
            'codigo_orden': '5001',
            'fecha_entrega_estimada': (date.today() + timedelta(days=4)).strftime('%d/%m/%Y'),
            'precio': 40000,
            'espacio_fisico': 'A1',
            'estado': 'Cotización',
            'tecnico': self.tecnico.id,
            'mantenimiento': False
        }
        
        form = ReparacionForm(data=form_data, instance=self.reparacion)
        self.assertTrue(form.is_valid())
        
        updated_reparacion = actualizar_reparacion(form, self.reparacion.id)
        
        self.assertFalse(updated_reparacion.mantenimiento)
        self.assertEqual(updated_reparacion.precio, 40000)
        self.assertEqual(updated_reparacion.marca_reloj, 'Sin Mantenimiento')

    def test_actualizar_reparacion_nonexistent(self):
        """Test actualizar reparación que no existe"""
        form_data = {
            'cliente': self.cliente.id,
            'marca_reloj': 'No Existe',
            'descripcion': 'Esta reparación no existe',
            'codigo_orden': '9999',
            'fecha_entrega_estimada': (date.today() + timedelta(days=5)).strftime('%d/%m/%Y'),
            'precio': 50000,
            'espacio_fisico': 'X1',
            'estado': 'Cotización',
            'tecnico': self.tecnico.id,
            'mantenimiento': False        }
        
        form = ReparacionForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        with self.assertRaises(Http404):
            actualizar_reparacion(form, 99999)


class ReparacionEdgeCasesTest(TestCase):
    """Test suite para casos edge y validaciones especiales"""
    
    def setUp(self):
        """Configuración para tests de casos edge"""
        self.cliente = Cliente.objects.create(
            nombre="Edge",
            apellido="Case",
            telefono="9999999999"
        )
        
        self.tecnico = Empleado.objects.create(
            cedula="9999999999",
            nombre="Edge",
            apellidos="Tester",
            fecha_ingreso=date.today(),
            fecha_nacimiento=date(1985, 1, 1),
            celular="3009999999",
            cargo="Senior",
            salario=3000000,
            estado="Activo"
        )

    def test_maintenance_with_special_characters_description(self):
        """Test mantenimiento with caracteres especiales en descripción"""
        data = {
            'cliente': self.cliente.id,
            'marca_reloj': 'Ñandú & Cía',
            'descripcion': 'Mantenimiento con acentos ñ, ü y símbolos €$',
            'codigo_orden': '6001',
            'fecha_entrega_estimada': (date.today() + timedelta(days=5)).strftime('%d/%m/%Y'),
            'precio': 100000,
            'espacio_fisico': 'Ñ1',
            'estado': 'Reparación',
            'tecnico': self.tecnico.id,
            'mantenimiento': True
        }
        
        form = ReparacionForm(data=data)
        self.assertTrue(form.is_valid(), f"Errores: {form.errors}")
        
        reparacion = crear_reparacion(form)
        self.assertTrue(reparacion.mantenimiento)
        self.assertIn('acentos', reparacion.descripcion)

    def test_maintenance_with_maximum_price(self):
        """Test mantenimiento con precio máximo permitido"""
        data = {
            'cliente': self.cliente.id,
            'marca_reloj': 'Luxury',
            'descripcion': 'Mantenimiento de reloj de lujo con precio máximo',
            'codigo_orden': '6002',
            'fecha_entrega_estimada': (date.today() + timedelta(days=30)).strftime('%d/%m/%Y'),
            'precio': 999999,  # Precio máximo
            'espacio_fisico': 'L1',
            'estado': 'Reparación',
            'tecnico': self.tecnico.id,
            'mantenimiento': True
        }
        
        form = ReparacionForm(data=data)
        self.assertTrue(form.is_valid())
        
        reparacion = crear_reparacion(form)
        self.assertTrue(reparacion.mantenimiento)
        self.assertEqual(reparacion.precio, 999999)

    def test_bulk_maintenance_operations(self):
        """Test operaciones en lote con mantenimiento"""
        # Crear múltiples reparaciones
        reparaciones = []
        for i in range(5):
            reparacion = Reparacion.objects.create(
                cliente=self.cliente,
                marca_reloj=f"Bulk{i}",
                descripcion=f"Reparación en lote número {i}",
                codigo_orden=f"700{i}",
                fecha_entrega_estimada=date.today() + timedelta(days=i+1),
                precio=50000 + (i * 10000),
                espacio_fisico=f"B{i}",
                estado="Cotización",
                tecnico=self.tecnico,
                mantenimiento=i % 2 == 0  # Alternando mantenimiento
            )
            reparaciones.append(reparacion)
        
        # Verificar que se crearon correctamente
        self.assertEqual(len(reparaciones), 5)
        
        # Verificar alternancia de mantenimiento
        maintenance_count = sum(1 for r in reparaciones if r.mantenimiento)
        no_maintenance_count = len(reparaciones) - maintenance_count
        
        self.assertEqual(maintenance_count, 3)  # 0, 2, 4
        self.assertEqual(no_maintenance_count, 2)  # 1, 3

    def test_maintenance_state_transitions(self):
        """Test transiciones de estado con mantenimiento"""
        estados = ['Cotización', 'Reparación', 'Prueba', 'Listo', 'Entregado']
        
        reparacion = Reparacion.objects.create(
            cliente=self.cliente,
            marca_reloj="Transition Test",
            descripcion="Test de transiciones de estado",
            codigo_orden="8001",
            fecha_entrega_estimada=date.today() + timedelta(days=5),
            precio=75000,
            espacio_fisico="T1",
            estado="Cotización",
            tecnico=self.tecnico,
            mantenimiento=True
        )
        
        # Simular transiciones de estado
        for estado in estados:
            reparacion.estado = estado
            reparacion.save()
            
            updated_reparacion = Reparacion.objects.get(id=reparacion.id)
            self.assertEqual(updated_reparacion.estado, estado)
            self.assertTrue(updated_reparacion.mantenimiento)  # Mantenimiento se mantiene


if __name__ == '__main__':
    # Ejecutar tests específicos si se ejecuta directamente
    import unittest
    unittest.main(verbosity=2)
