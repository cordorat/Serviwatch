from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from core.models.reloj import Reloj
from core.models.cliente import Cliente
from core.models.abono import Abono
from core.forms.reloj_form import RelojForm
from core.services.reloj_service import get_all_relojes, create_reloj
from decimal import Decimal
from datetime import date

class BaseRelojTestCase(TestCase):
    """Configuración base para todos los tests de reloj"""
    
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

        # Datos válidos para formularios
        self.valid_reloj_data = {
            'marca': 'Rolex',
            'referencia': 'TEST123',
            'precio': '15000',
            'dueno': 'Juan Pérez',
            'descripcion': 'Reloj de lujo',
            'tipo': 'NUEVO',
            'estado': 'DISPONIBLE',
            'tiene_comision': False
        }

        # Datos para venta
        self.valid_venta_data = {
            'marca': 'Rolex',
            'referencia': 'TEST123',
            'precio': '15000',
            'dueno': 'Juan Pérez',
            'descripcion': 'Reloj de lujo',
            'tipo': 'NUEVO',
            'estado': 'VENDIDO',
            'fecha_venta': date.today().strftime('%d/%m/%Y'),
            'cliente': self.cliente.id,
            'metodo_pago': 'CONTADO',
            'tiene_comision': False
        }

class RelojServiceTests(BaseRelojTestCase):
    """Tests para el servicio de relojes"""

    def test_get_all_relojes_vacio(self):
        """Test para obtener todos los relojes cuando no existen"""
        relojes = get_all_relojes()
        self.assertEqual(relojes.count(), 0)

    def test_get_all_relojes_con_datos(self):
        """Test para obtener todos los relojes cuando existen"""
        Reloj.objects.create(**self.valid_reloj_data)
        relojes = get_all_relojes()
        self.assertEqual(relojes.count(), 1)

    def test_create_reloj_exitoso(self):
        """Test para crear reloj exitosamente"""
        form = RelojForm(data=self.valid_reloj_data)
        self.assertTrue(form.is_valid())
        
        reloj = create_reloj(form)
        self.assertEqual(reloj.marca, 'Rolex')
        self.assertEqual(reloj.precio, '15000')
        self.assertEqual(reloj.saldo_pendiente, '15000')
        self.assertFalse(reloj.pagado)

    def test_create_reloj_con_comision(self):
        """Test para crear reloj con comisión"""
        data = self.valid_reloj_data.copy()
        data['tiene_comision'] = True
        
        form = RelojForm(data=data)
        self.assertTrue(form.is_valid())
        
        reloj = create_reloj(form)
        # Comisión debería ser 20% del precio
        self.assertEqual(reloj.comision, '3000')  # 15000 * 0.2

    def test_create_reloj_sin_comision(self):
        """Test para crear reloj sin comisión"""
        form = RelojForm(data=self.valid_reloj_data)
        self.assertTrue(form.is_valid())
        
        reloj = create_reloj(form)
        self.assertEqual(reloj.comision, '0')

class RelojFormTests(BaseRelojTestCase):
    """Tests para el formulario de relojes"""

    def test_form_valido_disponible(self):
        """Test para formulario válido con estado disponible"""
        form = RelojForm(data=self.valid_reloj_data)
        self.assertTrue(form.is_valid())

    def test_form_valido_vendido_contado(self):
        """Test para formulario válido con venta al contado"""
        form = RelojForm(data=self.valid_venta_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['pagado'], True)
        self.assertEqual(form.cleaned_data['saldo_pendiente'], '0')

    def test_form_valido_vendido_abono(self):
        """Test para formulario válido con venta por abono"""
        data = self.valid_venta_data.copy()
        data['metodo_pago'] = 'ABONO'
        
        form = RelojForm(data=data)
        self.assertTrue(form.is_valid())
        # La lógica de saldo_pendiente se maneja en las vistas
        self.assertFalse(form.cleaned_data['pagado'])

    def test_form_marca_requerida(self):
        """Test para validar que la marca es requerida"""
        data = self.valid_reloj_data.copy()
        del data['marca']
        
        form = RelojForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('marca', form.errors)

    def test_form_referencia_requerida(self):
        """Test para validar que la referencia es requerida"""
        data = self.valid_reloj_data.copy()
        del data['referencia']
        
        form = RelojForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('referencia', form.errors)

    def test_form_precio_requerido(self):
        """Test para validar que el precio es requerido"""
        data = self.valid_reloj_data.copy()
        del data['precio']
        
        form = RelojForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('precio', form.errors)

    def test_form_precio_numerico(self):
        """Test para validar que el precio sea numérico"""
        data = self.valid_reloj_data.copy()
        data['precio'] = 'abc'
        
        form = RelojForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('precio', form.errors)

    def test_form_precio_positivo(self):
        """Test para validar que el precio sea positivo"""
        data = self.valid_reloj_data.copy()
        data['precio'] = '-1000'
        
        form = RelojForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('precio', form.errors)

    def test_form_vendido_requiere_cliente(self):
        """Test para validar que al vender se requiere cliente"""
        data = self.valid_venta_data.copy()
        del data['cliente']
        
        form = RelojForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('cliente', form.errors)

    def test_form_vendido_requiere_fecha_venta(self):
        """Test para validar que al vender se requiere fecha de venta"""
        data = self.valid_venta_data.copy()
        del data['fecha_venta']
        
        form = RelojForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_venta', form.errors)

class RelojViewTests(BaseRelojTestCase):
    """Tests para las vistas de relojes"""

    def test_reloj_list_view_get(self):
        """Test GET request to reloj list view"""
        response = self.client.get(reverse('reloj_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reloj/reloj_list.html')
        self.assertIn('relojes', response.context)

    def test_reloj_list_view_con_datos(self):
        """Test reloj list view with data"""
        Reloj.objects.create(**self.valid_reloj_data)
        response = self.client.get(reverse('reloj_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_reloj_create_view_get(self):
        """Test GET request to reloj create view"""
        response = self.client.get(reverse('reloj_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reloj/reloj_form.html')
        self.assertIsInstance(response.context['form'], RelojForm)

    def test_reloj_create_view_post_valid(self):
        """Test POST request to reloj create view with valid data"""
        response = self.client.post(reverse('reloj_create'), data=self.valid_reloj_data)
        self.assertRedirects(response, reverse('reloj_list'))
        
        # Verificar que se creó el reloj
        self.assertTrue(Reloj.objects.filter(referencia='TEST123').exists())
        
        # Verificar mensaje de éxito
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Referencia de reloj agregada con éxito')

    def test_reloj_create_view_post_invalid(self):
        """Test POST request to reloj create view with invalid data"""
        data = self.valid_reloj_data.copy()
        data['precio'] = 'invalid'
        
        response = self.client.post(reverse('reloj_create'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reloj/reloj_form.html')
        self.assertFalse(response.context['form'].is_valid())

    def test_reloj_edit_view_get_valid(self):
        """Test GET request to update a valid reloj"""
        reloj = Reloj.objects.create(**self.valid_reloj_data)
        response = self.client.get(reverse('reloj_edit', kwargs={'pk': reloj.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reloj/reloj_form.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['modo'], 'editar')

    def test_reloj_edit_view_post_valid(self):
        """Test POST request with valid data updates the reloj"""
        reloj = Reloj.objects.create(**self.valid_reloj_data)
        updated_data = self.valid_reloj_data.copy()
        updated_data['marca'] = 'Omega'
        updated_data['descripcion'] = 'Actualizado'
        
        response = self.client.post(reverse('reloj_edit', kwargs={'pk': reloj.pk}), data=updated_data)
        self.assertRedirects(response, reverse('reloj_list'))
        
        # Verificar que se actualizó
        reloj.refresh_from_db()
        self.assertEqual(reloj.marca, 'Omega')
        self.assertEqual(reloj.descripcion, 'Actualizado')

    def test_reloj_edit_view_reloj_inexistente(self):
        """Test edit view with non-existent reloj"""
        response = self.client.get(reverse('reloj_edit', kwargs={'pk': 999999}))
        self.assertRedirects(response, reverse('reloj_list'))
        
        # Verificar mensaje de error
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'El reloj no existe.')

    def test_reloj_venta_view_get(self):
        """Test GET request to reloj venta view"""
        reloj = Reloj.objects.create(**self.valid_reloj_data)
        response = self.client.get(reverse('reloj_venta', kwargs={'pk': reloj.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reloj/reloj_form.html')
        self.assertEqual(response.context['modo'], 'vender')

    def test_reloj_venta_view_post_contado(self):
        """Test POST request for venta al contado"""
        reloj = Reloj.objects.create(**self.valid_reloj_data)
        response = self.client.post(reverse('reloj_venta', kwargs={'pk': reloj.pk}), data=self.valid_venta_data)
        self.assertRedirects(response, reverse('reloj_venta_list'))
        
        # Verificar que se vendió correctamente
        reloj.refresh_from_db()
        self.assertEqual(reloj.estado, 'VENDIDO')
        self.assertEqual(reloj.metodo_pago, 'CONTADO')
        self.assertTrue(reloj.pagado)
        self.assertEqual(reloj.saldo_pendiente, '0')

    def test_reloj_venta_view_post_abono(self):
        """Test POST request for venta por abono"""
        reloj = Reloj.objects.create(**self.valid_reloj_data)
        data = self.valid_venta_data.copy()
        data['metodo_pago'] = 'ABONO'
        
        response = self.client.post(reverse('reloj_venta', kwargs={'pk': reloj.pk}), data=data)
        self.assertRedirects(response, reverse('reloj_venta_list'))
        
        # Verificar que se vendió correctamente con abono
        reloj.refresh_from_db()
        self.assertEqual(reloj.estado, 'VENDIDO')
        self.assertEqual(reloj.metodo_pago, 'ABONO')
        self.assertFalse(reloj.pagado)
        self.assertEqual(reloj.saldo_pendiente, '15000')

    def test_usuario_no_autenticado(self):
        """Test that unauthenticated users are redirected"""
        self.client.logout()
        
        # Test list view
        response = self.client.get(reverse('reloj_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
        
        # Test create view
        response = self.client.get(reverse('reloj_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
