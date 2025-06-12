from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models.reloj import Reloj
from core.models.abono import Abono
from core.models.cliente import Cliente
from core.services.abono_service import calcular_saldo_pendiente, registrar_abono
from core.forms.abono_form import AbonoForm
from decimal import Decimal

class BaseTestCase(TestCase):
    def setUp(self):
        # Configuración base para todos los tests
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

        self.cliente = Cliente.objects.create(
            nombre='Juan',
            apellido='Pérez',
            telefono='1234567890'
        )

        self.reloj = Reloj.objects.create(
            marca='Rolex',
            referencia='TEST123',
            precio='1000',
            estado='VENDIDO',
            metodo_pago='ABONO',
            saldo_pendiente='1000',
            cliente=self.cliente
        )

class AbonoServiceTests(BaseTestCase):
    """Tests para el servicio de abonos"""

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

    def test_registrar_abono_exitoso(self):
        """Test para registrar abono exitosamente"""
        abono, reloj = registrar_abono(self.reloj.id, '300', 'Primer abono')
        self.assertEqual(abono.monto, '300')
        self.assertEqual(reloj.saldo_pendiente, '700')
        self.assertFalse(reloj.pagado)

    def test_registrar_abono_completo(self):
        """Test para registrar abono que completa el pago"""
        abono, reloj = registrar_abono(self.reloj.id, '1000', 'Pago final')
        self.assertEqual(reloj.saldo_pendiente, '0')
        self.assertTrue(reloj.pagado)

    def test_registrar_abono_monto_negativo(self):
        """Test para registrar abono con monto negativo"""
        with self.assertRaises(ValueError):
            registrar_abono(self.reloj.id, '-100')

    def test_registrar_abono_monto_excesivo(self):
        """Test para registrar abono con monto mayor al saldo"""
        with self.assertRaises(ValueError):
            registrar_abono(self.reloj.id, '2000')

    def test_registrar_abono_reloj_inexistente(self):
        """Test para registrar abono a reloj inexistente"""
        with self.assertRaises(ValueError):
            registrar_abono(999999, '100')

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

    def test_form_monto_cero(self):
        """Test para formulario con monto cero"""
        form = AbonoForm(data={'monto': '0'})
        self.assertFalse(form.is_valid())

    def test_form_monto_no_numerico(self):
        """Test para formulario con monto no numérico"""
        form = AbonoForm(data={'monto': 'abc'})
        self.assertFalse(form.is_valid())

    def test_form_monto_vacio(self):
        """Test para formulario con monto vacío"""
        form = AbonoForm(data={'monto': ''})
        self.assertFalse(form.is_valid())

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
        self.reloj.refresh_from_db()
        self.assertEqual(self.reloj.saldo_pendiente, '700')

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

    def test_metodo_no_permitido(self):
        """Test para método HTTP no permitido"""
        url = reverse('reloj_abono_create', args=[self.reloj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_usuario_no_autenticado(self):
        """Test para usuario no autenticado"""
        self.client.logout()
        url = reverse('reloj_abono_create', args=[self.reloj.id])
        response = self.client.post(url, {'monto': '100'})
        self.assertEqual(response.status_code, 302)