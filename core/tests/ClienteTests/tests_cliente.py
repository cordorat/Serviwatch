from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from core.models import Cliente
from core.forms.cliente_form import ClienteForm
from django.contrib.auth.models import User
from django.urls import reverse
import json

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

class ClienteListViewTest(TestCase):
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
        # Create some test clients
        Cliente.objects.create(
            nombre="Juan",
            apellido="Pérez",
            telefono="3001234567"
        )
        Cliente.objects.create(
            nombre="María",
            apellido="López",
            telefono="3007654321"
        )
        
        # Create a test client for HTTP requests
        self.client = Client()
        
        # Log in the test user
        self.client.login(username='testuser', password='testpassword')
    
    def test_view_url_exists_at_desired_location(self):
        """Test that the view exists at the correct URL"""
        response = self.client.get('/clientes/')  # Adjust this path to match your URL configuration
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        """Test that the view is accessible by its name"""
        response = self.client.get(reverse('cliente_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template"""
        response = self.client.get(reverse('cliente_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cliente/cliente_list.html')
    
    def test_view_contains_clients(self):
        """Test that the view contains the test clients"""
        response = self.client.get(reverse('cliente_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['clientes']), 2)
    
    def test_login_required(self):
        """Test that the view requires login"""
        # Log out the user
        self.client.logout()
        
        # Try to access the view
        response = self.client.get(reverse('cliente_list'))
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

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
        url = reverse('cliente_editar', kwargs={
            'nombre': self.test_cliente.nombre,
            'apellido': self.test_cliente.apellido,
            'telefono': self.test_cliente.telefono
        })
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
        url = reverse('cliente_editar', kwargs={
            'nombre': self.test_cliente.nombre,
            'apellido': self.test_cliente.apellido,
            'telefono': self.test_cliente.telefono
        })
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

class ClienteSearchViewTest(TestCase):
    
    def setUp(self):
        # Create some test clients
        Cliente.objects.create(
            nombre="Juan",
            apellido="Pérez",
            telefono="3001234567"
        )
        Cliente.objects.create(
            nombre="María",
            apellido="López",
            telefono="3007654321"
        )
        Cliente.objects.create(
            nombre="Pedro",
            apellido="Martínez",
            telefono="3005551234"
        )
        
        # Create a test client for HTTP requests
        self.client = Client()
    
    def test_search_by_nombre(self):
        """Test searching by nombre"""
        response = self.client.get(reverse('cliente_search'), {'term': 'Juan'})
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Should return one result
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['value'], 'Juan Pérez')
        self.assertEqual(data[0]['telefono'], '3001234567')
    
    def test_search_by_apellido(self):
        """Test searching by apellido"""
        response = self.client.get(reverse('cliente_search'), {'term': 'López'})
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Should return one result
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['value'], 'María López')
        self.assertEqual(data[0]['telefono'], '3007654321')
    
    def test_search_by_telefono(self):
        """Test searching by telefono"""
        response = self.client.get(reverse('cliente_search'), {'term': '3005551234'})
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Should return one result
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['value'], 'Pedro Martínez')
        self.assertEqual(data[0]['telefono'], '3005551234')
    
    def test_search_partial_match(self):
        """Test searching with a partial match"""
        response = self.client.get(reverse('cliente_search'), {'term': 'Mar'})
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Should return two results (María and Martínez)
        self.assertEqual(len(data), 2)
        
        # Check that the results contain the expected clients
        values = [item['value'] for item in data]
        self.assertIn('María López', values)
        self.assertIn('Pedro Martínez', values)
    
    def test_search_case_insensitive(self):
        """Test that search is case insensitive"""
        response = self.client.get(reverse('cliente_search'), {'term': 'juan'})  # Lowercase
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Should return one result
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['value'], 'Juan Pérez')
    
    def test_search_term_too_short(self):
        """Test that search terms shorter than 2 characters return empty results"""
        response = self.client.get(reverse('cliente_search'), {'term': 'J'})
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Should return empty list
        self.assertEqual(len(data), 0)
    
    def test_search_no_results(self):
        """Test searching with a term that has no matches"""
        response = self.client.get(reverse('cliente_search'), {'term': 'NoExiste'})
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Should return empty list
        self.assertEqual(len(data), 0)
    
    def test_search_response_format(self):
        """Test that the search response has the correct format"""
        response = self.client.get(reverse('cliente_search'), {'term': 'Juan'})
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Check the structure of the first result
        self.assertIn('id', data[0])
        self.assertIn('label', data[0])
        self.assertIn('value', data[0])
        self.assertIn('telefono', data[0])
        
        # Check the content of the first result
        self.assertEqual(data[0]['label'], 'Juan Pérez - 3001234567')
        self.assertEqual(data[0]['value'], 'Juan Pérez')
        self.assertEqual(data[0]['telefono'], '3001234567')