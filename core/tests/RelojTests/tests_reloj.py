from django.test import TestCase
from core.models.reloj import Reloj
from core.forms.reloj_form import RelojForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.contrib.messages import get_messages

class RelojFormTest(TestCase):

    def test_form_valid_data(self):
        """Test the form with valid data"""
        data = {
            'marca': 'Rolex',
            'referencia': '12345',
            'precio': 15000,
            'dueño': 'Juan Perez',
            'descripcion': 'Reloj de lujo',
            'tipo': 'NUEVO',
            'estado': 'DISPONIBLE',
            'fecha_venta': '',
            'pagado': False
        }

        form = RelojForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_data_marca_required(self):
        """Test the form with missing 'marca' field"""
        data = {
            'referencia': '12345',
            'precio': 15000,
            'dueño': 'Juan Perez',
            'descripcion': 'Reloj de lujo',
            'tipo': 'NUEVO',
            'estado': 'DISPONIBLE',
            'fecha_venta': '',
            'pagado': False
        }

        form = RelojForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('marca', form.errors)

    def test_form_invalid_data_precio_required(self):
        """Test the form with missing 'precio' field"""
        data = {
            'marca': 'Rolex',
            'referencia': '12345',
            'dueño': 'Juan Perez',
            'descripcion': 'Reloj de lujo',
            'tipo': 'NUEVO',
            'estado': 'DISPONIBLE',
            'fecha_venta': '',
            'pagado': False
        }

        form = RelojForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('precio', form.errors)

    def test_clean_precio_valid(self):
        """Test the clean_precio method for valid input"""
        data = {
            'marca': 'Rolex',
            'referencia': '12345',
            'precio': 15000,
            'dueño': 'Juan Perez',
            'descripcion': 'Reloj de lujo',
            'tipo': 'NUEVO',
            'estado': 'DISPONIBLE',
            'fecha_venta': '',
            'pagado': False
        }

        form = RelojForm(data=data)
        form.is_valid()
        self.assertEqual(form.cleaned_data['precio'], 15000)

    def test_clean_precio_invalid(self):
        """Test the clean_precio method for invalid input"""
        data = {
            'marca': 'Rolex',
            'referencia': '12345',
            'precio': 'invalid_value',  # Esto no es un número válido
            'dueño': 'Juan Perez',
            'descripcion': 'Reloj de lujo',
            'tipo': 'NUEVO',
            'estado': 'DISPONIBLE',
            'fecha_venta': '',
            'pagado': False
        }

        form = RelojForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('precio', form.errors)

    def test_clean_precio_negative(self):
        """Test the clean_precio method for negative values"""
        data = {
            'marca': 'Rolex',
            'referencia': '12345',
            'precio': -15000,  # Precio negativo
            'dueño': 'Juan Perez',
            'descripcion': 'Reloj de lujo',
            'tipo': 'NUEVO',
            'estado': 'DISPONIBLE',
            'fecha_venta': '',
            'pagado': False
        }

        form = RelojForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('precio', form.errors)

    def test_clean_precio_too_large(self):
        """Test the clean_precio method for values that are too large"""
        data = {
            'marca': 'Rolex',
            'referencia': '12345',
            'precio': 1000000000000,  # Precio demasiado grande
            'dueño': 'Juan Perez',
            'descripcion': 'Reloj de lujo',
            'tipo': 'NUEVO',
            'estado': 'DISPONIBLE',
            'fecha_venta': '',
            'pagado': False
        }

        form = RelojForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('precio', form.errors)

    def test_clean_fecha_venta_required_when_estado_is_vendido(self):
        """Test that fecha_venta is required when estado is 'VENDIDO'"""
        data = {
            'marca': 'Rolex',
            'referencia': '12345',
            'precio': 15000,
            'dueño': 'Juan Perez',
            'descripcion': 'Reloj de lujo',
            'tipo': 'NUEVO',
            'estado': 'VENDIDO',
            'fecha_venta': '',  # Debería ser obligatorio
            'pagado': False
        }

        form = RelojForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_venta', form.errors)

    def test_form_fecha_venta_format(self):
        data = {
            'marca': 'Rolex',
            'referencia': '12345',
            'precio': 15000,
            'dueño': 'Juan Perez',
            'descripcion': 'Reloj de lujo',
            'tipo': 'NUEVO',
            'estado': 'VENDIDO',
            'fecha_venta': '31-12-2025',  # Formato inválido
            'pagado': False
        }

        form = RelojForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_venta', form.errors)

    def test_clean_fecha_venta_valid(self):
        """Test valid fecha_venta format"""
        data = {
            'marca': 'Rolex',
            'referencia': '12345',
            'precio': 15000,
            'dueño': 'Juan Perez',
            'descripcion': 'Reloj de lujo',
            'tipo': 'NUEVO',
            'estado': 'VENDIDO',
            'fecha_venta': '10/10/2025',  # Formato válido
            'pagado': False
        }

        form = RelojForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_data_dueño_required(self):
        """Test the form with missing 'dueño' field"""
        data = {
            'marca': 'Rolex',
            'referencia': '12345',
            'precio': 15000,
            'descripcion': 'Reloj de lujo',
            'tipo': 'NUEVO',
            'estado': 'DISPONIBLE',
            'fecha_venta': '',
            'pagado': False
        }

        form = RelojForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('dueño', form.errors)

class RelojViewsTest(TestCase):
    def setUp(self):
        """Set up test environment"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        
        # Create sample reloj data
        self.valid_reloj_data = {
            'marca': 'Rolex',
            'referencia': '12345',
            'precio': '15000',
            'dueño': 'Juan Perez',
            'descripcion': 'Reloj de lujo',
            'tipo': 'NUEVO',
            'estado': 'DISPONIBLE',
            'fecha_venta': '',
            'pagado': False
        }
        
        # Create multiple relojes for pagination testing
        for i in range(7):
            Reloj.objects.create(
                marca=f'Marca{i}',
                referencia=f'REF{i}',
                precio=1000 * i,
                dueño='Test Owner',
                tipo='NUEVO',
                estado='DISPONIBLE'
            )

    def test_reloj_list_view_authenticated(self):
        """Test reloj list view when user is authenticated"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('reloj_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reloj/reloj_list.html')
        self.assertTrue('relojes' in response.context)
        self.assertTrue('is_paginated' in response.context)
        self.assertEqual(len(response.context['page_obj']), 6)  # Check pagination

    def test_reloj_create_view_get(self):
        """Test GET request to reloj create view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('reloj_create'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reloj/reloj_form.html')
        self.assertTrue(isinstance(response.context['form'], RelojForm))

    def test_reloj_create_view_post_valid(self):
        """Test POST request to reloj create view with valid data"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('reloj_create'), data=self.valid_reloj_data)
        
        self.assertRedirects(response, reverse('reloj_list'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Referencia de reloj agregada con éxito')

    def test_reloj_create_view_post_invalid(self):
        """Test POST request to reloj create view with invalid data"""
        self.client.login(username='testuser', password='testpass123')
        invalid_data = self.valid_reloj_data.copy()
        invalid_data.pop('marca')  # Remove required field
        
        response = self.client.post(reverse('reloj_create'), data=invalid_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reloj/reloj_form.html')
        self.assertTrue(response.context['form'].errors)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Por favor corrige los errores en el formulario.')

    def test_reloj_list_pagination(self):
        """Test pagination of reloj list"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test first page
        response = self.client.get(reverse('reloj_list'))
        self.assertEqual(len(response.context['page_obj']), 6)
        self.assertTrue(response.context['is_paginated'])
        
        # Test second page
        response = self.client.get(f"{reverse('reloj_list')}?page=2")
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertTrue(response.context['is_paginated'])