from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from core.models import Cliente
from core.forms.cliente_form import ClienteForm
from django.contrib.auth.models import User
from django.urls import reverse
import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.contrib.messages import get_messages

class ClienteModelTest(TestCase):

    def test_crear_cliente_valido(self):
        cliente = Cliente.objects.create(
            nombre='Juan',
            apellido='Pérez',
            telefono='3001234567'
        )
        self.assertEqual(cliente.nombre, 'Juan')
        self.assertEqual(cliente.apellido, 'Pérez')
        self.assertEqual(cliente.telefono, '3001234567')

    def test_error_si_falta_nombre(self):
        cliente = Cliente(
            apellido='Pérez',
            telefono='3001234567'
        )
        with self.assertRaises(ValidationError):
            cliente.full_clean() 

    def test_telefono_con_letras_no_valido(self):
        cliente = Cliente(
            nombre='Ana',
            apellido='López',
            telefono='ABC1234567'
        )
        with self.assertRaises(ValidationError):
            cliente.full_clean()

    def test_telefono_muy_corto(self):
        cliente = Cliente(
            nombre='Carlos',
            apellido='Ramírez',
            telefono='123'
        )
        with self.assertRaises(ValidationError):
            cliente.full_clean()

class ClienteFormTest(TestCase):
    
    def setUp(self):
        # Create a test client to use for duplicate validation
        self.existing_client = Cliente.objects.create(
            nombre="Existente",
            apellido="Cliente",
            telefono="3001234567"
        )
    
    def test_form_data_valida(self):
        """Test that the form is valid with correct data"""
        form_data = {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'telefono': '3001234567'
        }
        form = ClienteForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_data_vacia(self):
        """Test that the form is invalid with empty data"""
        form_data = {
            'nombre': '',
            'apellido': '',
            'telefono': ''
        }
        form = ClienteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)
        self.assertIn('apellido', form.errors)
        self.assertIn('telefono', form.errors)
        self.assertEqual(form.errors['nombre'][0], 'El nombre es obligatorio.')
        self.assertEqual(form.errors['apellido'][0], 'El apellido es obligatorio.')
        self.assertEqual(form.errors['telefono'][0], 'El número de teléfono es obligatorio.')
    
    def test_nombre_dolo_letras(self):
        """Test that nombre only accepts letters"""
        form_data = {
            'nombre': 'Juan123',
            'apellido': 'Pérez',
            'telefono': '3001234567'
        }
        form = ClienteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)
        self.assertEqual(form.errors['nombre'][0], 'El nombre solo debe contener letras.')
    
    def test_apellido_solo_letras(self):
        """Test that apellido only accepts letters"""
        form_data = {
            'nombre': 'Juan',
            'apellido': 'Pérez123',
            'telefono': '3001234567'
        }
        form = ClienteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('apellido', form.errors)
        self.assertEqual(form.errors['apellido'][0], 'El apellido solo debe contener letras.')
    
    def test_telefono_solo_numeros(self):
        """Test that telefono only accepts digits"""
        form_data = {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'telefono': '300123456A'
        }
        form = ClienteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('telefono', form.errors)
        self.assertEqual(form.errors['telefono'][0], 'El número de teléfono solo debe contener números.')
    
    def test_telefono_tamaño(self):
        """Test that telefono must be exactly 10 digits"""
        # Test too short
        form_data = {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'telefono': '30012345'
        }
        form = ClienteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('telefono', form.errors)
        self.assertEqual(form.errors['telefono'][0], 'El número de teléfono debe tener exactamente 10 dígitos.')
    
    def test_cliente_duplicado(self):
        """Test that the form detects duplicate clients"""
        form_data = {
            'nombre': 'EXISTENTE',
            'apellido': 'Cliente',
            'telefono': '3001234567'
        }
        form = ClienteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)
        self.assertEqual(form.errors['nombre'][0], 'Este cliente ya esta registrado.')

class ClienteViewTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        
        # Crear algunos clientes de prueba
        self.cliente1 = Cliente.objects.create(
            nombre="Juan",
            apellido="Pérez",
            telefono="3001234567"
        )
        self.cliente2 = Cliente.objects.create(
            nombre="María",
            apellido="López",
            telefono="3007654321"
        )
        
        # URLs
        self.list_url = reverse('cliente_list')
        self.create_url = reverse('cliente_create')
        self.edit_url = reverse('cliente_editar', kwargs={'id': self.cliente1.id})

    def test_list_view_basic(self):
        """Test básico de la vista de lista"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cliente/cliente_list.html')
        self.assertTrue('clientes' in response.context)

    def test_list_view_search(self):
        """Test de búsqueda en la vista de lista"""
        response = self.client.get(self.list_url, {'term': 'Juan'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['clientes']), 1)
        
        # Búsqueda con múltiples términos
        response = self.client.get(self.list_url, {'term': 'Juan Pérez'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['clientes']), 1)

    def test_list_view_no_results(self):
        """Test de búsqueda sin resultados"""
        response = self.client.get(self.list_url, {'term': 'NoExiste'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['no_results'])

    def test_create_view_get(self):
        """Test de la vista de creación (GET)"""
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cliente/cliente_form.html')
        self.assertEqual(response.context['modo'], 'agregar')

    def test_create_view_post_success(self):
        """Test de creación exitosa de cliente"""
        data = {
            'nombre': 'Nuevo',
            'apellido': 'Cliente',
            'telefono': '3009876543'
        }
        response = self.client.post(self.create_url, data)
        self.assertRedirects(response, self.list_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Cliente creado exitosamente.')

    def test_edit_view_get(self):
        """Test de la vista de edición (GET)"""
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['modo'], 'editar')

    def test_edit_view_post_success(self):
        """Test de edición exitosa de cliente"""
        data = {
            'nombre': 'JuanEditado',
            'apellido': 'PérezEditado',
            'telefono': '3001234567'
        }
        response = self.client.post(self.edit_url, data)
        self.assertRedirects(response, self.list_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Cliente editado exitosamente.')

    def test_create_view_post_invalid(self):
        """Test de creación con datos inválidos"""
        data = {
            'nombre': 'Nuevo123',  # Inválido: contiene números
            'apellido': 'Cliente',
            'telefono': '3009876543'
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())

    def test_redirect_with_next_parameter(self):
        """Test de redirección con parámetro next"""
        data = {
            'nombre': 'Nuevo',
            'apellido': 'Cliente',
            'telefono': '3009876543'
        }
        # Usar una URL que exista en tu aplicación, por ejemplo la lista de clientes
        response = self.client.post(
            f"{self.create_url}?next={self.list_url}",
            data
        )
        # Verificar la redirección
        self.assertRedirects(response, self.list_url)

    def test_login_required(self):
        """Test que la vista requiere login"""
        self.client.logout()
        response = self.client.get(self.list_url)
        # Solo verificamos que redirija a login, sin verificar la página de destino
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login/' in response.url)

class ClienteCreateViewTest(TestCase):
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
        # Create a test client for HTTP requests
        self.client = Client()
        
        # Log in the test user
        self.client.login(username='testuser', password='testpassword')
        
        # Create a test client for editing
        self.test_cliente = Cliente.objects.create(
            nombre="Editar",
            apellido="Cliente",
            telefono="3009876543"
        )
    
    def test_view_url_accessible_by_name(self):
        """Test that the view is accessible by its name"""
        response = self.client.get(reverse('cliente_create'))
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template"""
        response = self.client.get(reverse('cliente_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cliente/cliente_form.html')
    
    def test_view_contains_form(self):
        """Test that the view contains the form"""
        response = self.client.get(reverse('cliente_create'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], ClienteForm)
    
    def test_view_mode_is_agregar_for_new_client(self):
        """Test that the view mode is 'agregar' for a new client"""
        response = self.client.get(reverse('cliente_create'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['modo'], 'agregar')
    
    def test_view_mode_is_editar_for_existing_client(self):
        """Test that the view mode is 'editar' for an existing client"""
        url = reverse('cliente_editar', kwargs={'id': self.test_cliente.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['modo'], 'editar')
    
    def test_create_new_client(self):
        """Test creating a new client"""
        form_data = {
            'nombre': 'Nuevo',
            'apellido': 'Cliente',
            'telefono': '3001112233'
        }
        response = self.client.post(reverse('cliente_create'), form_data)
        
        # Should redirect to cliente_list
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cliente_list'))
        
        # Check that the client was created
        self.assertTrue(Cliente.objects.filter(
            nombre='Nuevo',
            apellido='Cliente',
            telefono='3001112233'
        ).exists())
    
    def test_edit_existing_client(self):
        """Test editing an existing client"""
        # Use the client's ID instead of name/surname/phone
        url = reverse('cliente_editar', kwargs={'id': self.test_cliente.id})
        
        form_data = {
            'nombre': 'Editado',
            'apellido': 'Actualizado',
            'telefono': '3009876543'
        }
        response = self.client.post(url, form_data)
        
        # Should redirect to cliente_list
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cliente_list'))
        
        # Check that the client was updated
        self.test_cliente.refresh_from_db()
        self.assertEqual(self.test_cliente.nombre, 'Editado')
        self.assertEqual(self.test_cliente.apellido, 'Actualizado')
    
    def test_invalid_form_submission(self):
        """Test submitting an invalid form"""
        form_data = {
            'nombre': 'Nuevo123',  # Invalid: contains numbers
            'apellido': 'Cliente',
            'telefono': '3001112233'
        }
        response = self.client.post(reverse('cliente_create'), form_data)
        
        # Should stay on the same page
        self.assertEqual(response.status_code, 200)
        
        # Should contain form errors
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('nombre', response.context['form'].errors)
    
    def test_redirect_to_next_url(self):
        """Test redirecting to the 'next' URL parameter"""
        form_data = {
            'nombre': 'Nuevo',
            'apellido': 'Cliente',
            'telefono': '3001112233'
        }
        response = self.client.post(
            f"{reverse('cliente_create')}?next=/custom-redirect/",
            form_data
        )
        
        # Should redirect to the custom URL
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/custom-redirect/')
    
    def test_login_required(self):
        """Test that the view requires login"""
        # Log out the user
        self.client.logout()
        
        # Try to access the view
        response = self.client.get(reverse('cliente_create'))
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

