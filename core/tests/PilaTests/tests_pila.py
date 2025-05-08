from django.test import TestCase, Client
from django.urls import reverse
from core.models.pilas import Pilas
from core.services.pilas_service import get_pilas_paginated, create_pila
from core.forms.pila_form import PilasForm
from django.core.paginator import Page
from unittest.mock import MagicMock
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

class PilasModelTest(TestCase):
    def setUp(self):
        self.pila = Pilas.objects.create(
            codigo="CR2032",
            precio="1500",
            cantidad="10"
        )
    
    def test_pila_creation(self):
        """Test that a battery can be created with the required fields"""
        self.assertEqual(self.pila.codigo, "CR2032")
        self.assertEqual(self.pila.precio, "1500")
        self.assertEqual(self.pila.cantidad, "10")
    
    def test_str_representation(self):
        """Test the string representation of the battery"""
        self.assertEqual(str(self.pila), "CR2032 - 1500 - 10")
    
    def test_unique_codigo(self):
        """Test that codigo must be unique"""
        with self.assertRaises(Exception):
            Pilas.objects.create(
                codigo="CR2032",  # Same as the one in setUp
                precio="2000",
                cantidad="5"
            )

class PilasServiceTest(TestCase):
    def setUp(self):
        # Create 10 test batteries
        for i in range(10):
            Pilas.objects.create(
                codigo=f"CR20{i}",
                precio=f"{1000 + i}",
                cantidad=f"{i+1}"
            )
    
    def test_get_pilas_paginated_default(self):
        """Test that pagination works with default parameters"""
        result = get_pilas_paginated()
        self.assertIsInstance(result, Page)
        self.assertEqual(len(result), 6)  # Default items per page
        self.assertEqual(result.number, 1)  # First page by default
    
    def test_get_pilas_paginated_with_page(self):
        """Test pagination with specific page"""
        result = get_pilas_paginated(2)
        self.assertEqual(result.number, 2)
        self.assertEqual(len(result), 4)  # 10 total items, 6 on first page, 4 on second
    
    def test_create_pila(self):
        """Test creating a battery"""
        # Mock a valid form
        mock_form = MagicMock()
        mock_form.save.return_value = Pilas(codigo="TEST123", precio="1000", cantidad="5")
        
        result = create_pila(mock_form)
        self.assertEqual(result.codigo, "TEST123")
        mock_form.save.assert_called_once()

class PilasViewTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = Client()
        self.client.login(username='testuser', password='12345')
        
        # Create some test batteries
        for i in range(3):
            Pilas.objects.create(
                codigo=f"CR20{i}",
                precio=f"{1000 + i}",
                cantidad=f"{i+1}"
            )
        
        # Define URLs
        self.list_url = reverse('pilas_list')
        self.create_url = reverse('pilas_form')

    def test_pilas_list_view_authenticated(self):
        """Test that authenticated users can access the list view"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pilas/pilas_list.html')
        self.assertTrue('pilas' in response.context)
        self.assertEqual(len(response.context['pilas']), 3)

    def test_pila_create_view_get(self):
        """Test that the create view loads the form correctly"""
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pilas/pila_form.html')
        self.assertTrue('form' in response.context)

    def test_pila_create_view_post_success(self):
        """Test successful battery creation"""
        data = {
            'codigo': 'CR2050',
            'precio': '1500',
            'cantidad': '25'
        }
        response = self.client.post(self.create_url, data)
        self.assertRedirects(response, self.list_url)
        
        # Check that battery was created
        self.assertTrue(Pilas.objects.filter(codigo='CR2050').exists())
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Referencia de pila agregada con éxito')

    def test_pila_create_view_post_invalid(self):
        """Test with invalid form data"""
        data = {
            'codigo': 'CR2050',
            'precio': 'invalid',  # Should be numeric
            'cantidad': '25'
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pilas/pila_form.html')
        self.assertTrue('form' in response.context)
        self.assertFalse(response.context['form'].is_valid())
        self.assertFalse(Pilas.objects.filter(codigo='CR2050').exists())

class PilasFormTest(TestCase):
    def setUp(self):
        # Create a battery for testing unique code validation
        Pilas.objects.create(
            codigo="CR2032",
            precio="1500",
            cantidad="10"
        )

    def test_valid_form(self):
        """Test that the form validates with correct data"""
        data = {
            'codigo': 'CR2025', 
            'precio': '1500',
            'cantidad': '20'
        }
        form = PilasForm(data)
        self.assertTrue(form.is_valid())

    def test_codigo_unique_validation(self):
        """Test that the form validates codigo uniqueness"""
        data = {
            'codigo': 'CR2032',  # Already exists in setUp
            'precio': '2000',
            'cantidad': '5'
        }
        form = PilasForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['codigo'], ['Este codigo ya esta registrado'])

    def test_precio_numeric_validation(self):
        """Test that precio must be numeric"""
        data = {
            'codigo': 'CR2026',
            'precio': 'abc',  # Invalid: non-numeric
            'cantidad': '5'
        }
        form = PilasForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['precio'], ['El precio solo debe contener números.'])

    def test_cantidad_numeric_validation(self):
        """Test that cantidad must be numeric"""
        data = {
            'codigo': 'CR2027',
            'precio': '1200',
            'cantidad': 'xyz'  # Invalid: non-numeric
        }
        form = PilasForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['cantidad'], ['La cantidad solo debe contener números.'])

    def test_required_fields(self):
        """Test that all fields are required"""
        form = PilasForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['codigo'], ['El codigo es obligatorio'])
        self.assertEqual(form.errors['precio'], ['El precio es obligatorio'])
        self.assertEqual(form.errors['cantidad'], ['La cantidad es obligatorio'])