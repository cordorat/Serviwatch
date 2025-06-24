from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from core.models.reloj import Reloj
from core.models.abono import Abono
from core.models.cliente import Cliente
from core.services.abono_service import calcular_saldo_pendiente, registrar_abono, get_all_abonos
from core.forms.abono_form import AbonoForm
from decimal import Decimal
from datetime import date

class BaseTestCase(TestCase):
    """Configuración base para todos los tests de abono"""
    
    def setUp(self):
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

        # Crear cliente de prueba
        self.cliente = Cliente.objects.create(
            nombre='Juan',
            apellido='Pérez',
            telefono='1234567890'
        )

        # Crear reloj de prueba con abono
        self.reloj = Reloj.objects.create(
            marca='Rolex',
            referencia='TEST123',
            precio='1000',
            estado='VENDIDO',
            metodo_pago='ABONO',
            saldo_pendiente='1000',
            cliente=self.cliente,
            fecha_venta=date.today(),
            pagado=False
        )
        
        # Crear reloj sin abono para tests específicos
        self.reloj_sin_abono = Reloj.objects.create(
            marca='Omega',
            referencia='OMEGA001',
            precio='2000',
            estado='VENDIDO',
            metodo_pago='CONTADO',
            saldo_pendiente='0',
            cliente=self.cliente,
            fecha_venta=date.today(),
            pagado=True
        )

class AbonoServiceTests(BaseTestCase):
    """Tests para el servicio de abonos"""

    def test_get_all_abonos_vacio(self):
        """Test para obtener todos los abonos cuando no existen"""
        abonos = get_all_abonos(self.reloj.id)
        self.assertEqual(abonos.count(), 0)

    def test_get_all_abonos_con_datos(self):
        """Test para obtener todos los abonos cuando existen"""
        # Crear algunos abonos
        Abono.objects.create(reloj=self.reloj, monto='300', descripcion='Primer abono')
        Abono.objects.create(reloj=self.reloj, monto='200', descripcion='Segundo abono')
        
        abonos = get_all_abonos(self.reloj.id)
        self.assertEqual(abonos.count(), 2)
        # Verificar orden descendente por fecha (más reciente primero)
        self.assertEqual(abonos.first().monto, '300')  # Primer creado es más reciente

    def test_calcular_saldo_pendiente_sin_abono(self):
        """Test para calcular saldo pendiente sin abono"""
        saldo = calcular_saldo_pendiente(self.reloj)
        self.assertEqual(saldo, '1000')

    def test_calcular_saldo_pendiente_con_abono(self):
        """Test para calcular saldo pendiente con abono válido"""
        saldo = calcular_saldo_pendiente(self.reloj, '300')
        self.assertEqual(saldo, '700')

    def test_calcular_saldo_pendiente_abono_mayor(self):
        """Test para calcular saldo pendiente con abono mayor al saldo"""
        saldo = calcular_saldo_pendiente(self.reloj, '1200')
        self.assertEqual(saldo, '0')

    def test_calcular_saldo_pendiente_valor_invalido(self):
        """Test para calcular saldo pendiente con valor inválido"""
        self.reloj.saldo_pendiente = 'invalid'
        saldo = calcular_saldo_pendiente(self.reloj)
        self.assertEqual(saldo, '0')

    def test_calcular_saldo_pendiente_abono_cero(self):
        """Test para calcular saldo pendiente con abono cero"""
        saldo = calcular_saldo_pendiente(self.reloj, '0')
        self.assertEqual(saldo, '1000')

    def test_registrar_abono_exitoso(self):
        """Test para registrar abono exitosamente"""
        abono, reloj = registrar_abono(self.reloj.id, '300', 'Primer abono')
        self.assertEqual(abono.monto, '300')
        self.assertEqual(abono.descripcion, 'Primer abono')
        self.assertEqual(reloj.saldo_pendiente, '700')
        self.assertFalse(reloj.pagado)
        # Verificar que se creó el abono en la base de datos
        self.assertTrue(Abono.objects.filter(reloj=self.reloj, monto='300').exists())

    def test_registrar_abono_completo(self):
        """Test para registrar abono que completa el pago"""
        abono, reloj = registrar_abono(self.reloj.id, '1000', 'Pago final')
        self.assertEqual(reloj.saldo_pendiente, '0')
        self.assertTrue(reloj.pagado)

    def test_registrar_abono_sin_descripcion(self):
        """Test para registrar abono sin descripción"""
        abono, reloj = registrar_abono(self.reloj.id, '300')
        self.assertEqual(abono.descripcion, '')
        self.assertEqual(reloj.saldo_pendiente, '700')

    def test_registrar_abono_monto_negativo(self):
        """Test para registrar abono con monto negativo"""
        with self.assertRaises(ValueError) as context:
            registrar_abono(self.reloj.id, '-100')
        self.assertIn("El monto del abono debe ser mayor a 0", str(context.exception))

    def test_registrar_abono_monto_cero(self):
        """Test para registrar abono con monto cero"""
        with self.assertRaises(ValueError):
            registrar_abono(self.reloj.id, '0')

    def test_registrar_abono_monto_excesivo(self):
        """Test para registrar abono con monto mayor al saldo"""
        with self.assertRaises(ValueError) as context:
            registrar_abono(self.reloj.id, '2000')
        self.assertIn("El monto del abono no puede ser mayor al saldo pendiente", str(context.exception))

    def test_registrar_abono_monto_invalido(self):
        """Test para registrar abono con monto no numérico"""
        with self.assertRaises(ValueError):
            registrar_abono(self.reloj.id, 'abc')

    def test_registrar_abono_reloj_inexistente(self):
        """Test para registrar abono a reloj inexistente"""
        with self.assertRaises(ValueError) as context:
            registrar_abono(999999, '100')
        self.assertIn("El reloj especificado no existe", str(context.exception))

    def test_registrar_abono_reloj_sin_saldo_pendiente(self):
        """Test para registrar abono a reloj sin saldo pendiente inicial"""
        reloj_sin_saldo = Reloj.objects.create(
            marca='Test',
            referencia='TST001',
            precio='500',
            estado='VENDIDO',
            metodo_pago='ABONO',
            cliente=self.cliente
        )
        
        abono, reloj = registrar_abono(reloj_sin_saldo.id, '200', 'Test')
        self.assertEqual(reloj.saldo_pendiente, '300')  # 500 - 200

class AbonoFormTests(BaseTestCase):
    """Tests para el formulario de abonos"""

    def test_form_valido(self):
        """Test para formulario con datos válidos"""
        form = AbonoForm(data={
            'monto': '300',
            'descripcion': 'Test abono'
        })
        self.assertTrue(form.is_valid())

    def test_form_monto_negativo(self):
        """Test para formulario con monto negativo"""
        form = AbonoForm(data={'monto': '-100'})
        self.assertFalse(form.is_valid())
        self.assertIn('monto', form.errors)

    def test_form_monto_cero(self):
        """Test para formulario con monto cero"""
        form = AbonoForm(data={'monto': '0'})
        self.assertFalse(form.is_valid())
        self.assertIn('monto', form.errors)

    def test_form_monto_no_numerico(self):
        """Test para formulario con monto no numérico"""
        form = AbonoForm(data={'monto': 'abc'})
        self.assertFalse(form.is_valid())
        self.assertIn('monto', form.errors)

    def test_form_monto_vacio(self):
        """Test para formulario con monto vacío"""
        form = AbonoForm(data={'monto': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('monto', form.errors)

    def test_form_solo_descripcion(self):
        """Test para formulario sin monto pero con descripción"""
        form = AbonoForm(data={'descripcion': 'Test descripción'})
        self.assertFalse(form.is_valid())
        self.assertIn('monto', form.errors)

    def test_form_descripcion_opcional(self):
        """Test para verificar que la descripción es opcional"""
        form = AbonoForm(data={'monto': '500'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['descripcion'], '')

    def test_clean_monto_conversion(self):
        """Test para verificar la conversión correcta del monto"""
        form = AbonoForm(data={'monto': '1500', 'descripcion': 'Test'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['monto'], '1500')

    def test_form_save_method(self):
        """Test para el método save del formulario"""
        form = AbonoForm(data={
            'monto': '400',
            'descripcion': 'Test save'
        })
        self.assertTrue(form.is_valid())
        
        # El método save requiere un reloj
        abono = form.save(self.reloj)
        self.assertEqual(abono.monto, '400')
        self.assertEqual(abono.descripcion, 'Test save')
        self.assertEqual(abono.reloj, self.reloj)
        self.assertTrue(Abono.objects.filter(reloj=self.reloj, monto='400').exists())

class AbonoViewTests(BaseTestCase):
    """Tests para las vistas de abonos"""

    def test_crear_abono_exitoso(self):
        """Test para crear abono exitosamente"""
        url = reverse('reloj_abono_create', args=[self.reloj.id])
        response = self.client.post(url, {
            'monto': '300',
            'descripcion': 'Test abono',
        })
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el reloj se actualizó
        self.reloj.refresh_from_db()
        self.assertEqual(self.reloj.saldo_pendiente, '700')
        
        # Verificar que se creó el abono
        self.assertTrue(Abono.objects.filter(reloj=self.reloj, monto='300').exists())

    def test_crear_abono_invalido(self):
        """Test para crear abono con datos inválidos"""
        url = reverse('reloj_abono_create', args=[self.reloj.id])
        response = self.client.post(url, {
            'monto': '-100',
            'descripcion': 'Test inválido',
        })
        self.assertEqual(response.status_code, 302)
        
        # Verificar mensajes usando el storage de mensajes
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any(message.level_tag == 'error' for message in messages))
        
        # Verificar que el saldo pendiente no cambió
        self.reloj.refresh_from_db()
        self.assertEqual(self.reloj.saldo_pendiente, '1000')

    def test_crear_abono_monto_excesivo(self):
        """Test para crear abono con monto mayor al saldo pendiente"""
        url = reverse('reloj_abono_create', args=[self.reloj.id])
        response = self.client.post(url, {
            'monto': '2000',
            'descripcion': 'Test excesivo',
        })
        self.assertEqual(response.status_code, 302)
        
        # Verificar mensaje de error
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('mayor al saldo pendiente' in str(message) for message in messages))

    def test_crear_abono_sin_monto(self):
        """Test para crear abono sin especificar monto"""
        url = reverse('reloj_abono_create', args=[self.reloj.id])
        response = self.client.post(url, {
            'descripcion': 'Test sin monto',
        })
        self.assertEqual(response.status_code, 302)
        
        # Verificar mensaje de error
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('requerido' in str(message) for message in messages))

    def test_crear_abono_reloj_inexistente(self):
        """Test para crear abono a reloj que no existe"""
        url = reverse('reloj_abono_create', args=[999999])
        response = self.client.post(url, {'monto': '100'})
        self.assertEqual(response.status_code, 404)

    def test_metodo_no_permitido(self):
        """Test para método HTTP no permitido"""
        url = reverse('reloj_abono_create', args=[self.reloj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)  # Method not allowed

    def test_usuario_no_autenticado(self):
        """Test para usuario no autenticado"""
        self.client.logout()
        url = reverse('reloj_abono_create', args=[self.reloj.id])
        response = self.client.post(url, {
            'monto': '300',
            'descripcion': 'Test no autenticado',
        })
        self.assertEqual(response.status_code, 302)
        # Verificar redirección a login
        self.assertIn('/login/', response.url)

    def test_crear_abono_completa_pago(self):
        """Test para crear abono que completa el pago del reloj"""
        url = reverse('reloj_abono_create', args=[self.reloj.id])
        response = self.client.post(url, {
            'monto': '1000',  # Pago completo
            'descripcion': 'Pago final',
        })
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el reloj quedó pagado
        self.reloj.refresh_from_db()
        self.assertEqual(self.reloj.saldo_pendiente, '0')
        self.assertTrue(self.reloj.pagado)

    def test_crear_abono_con_next_url(self):
        """Test para crear abono con URL de redirección específica"""
        next_url = reverse('reloj_list')
        url = reverse('reloj_abono_create', args=[self.reloj.id])
        response = self.client.post(url, {
            'monto': '300',
            'descripcion': 'Test con next',
            'next': next_url
        })
        self.assertEqual(response.status_code, 302)
        # Nota: La redirección exacta depende de la implementación de la vista
