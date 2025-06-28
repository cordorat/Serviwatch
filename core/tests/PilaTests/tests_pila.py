"""
Tests simplificados para el módulo de Pilas.
Cobertura esencial con tests concisos y mantenibles.

Convenciones:
- Nombres de métodos y variables en inglés (PEP 8)
- Comentarios y documentación en español
- Tests enfocados en casos principales
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages
from django.db import IntegrityError
from unittest.mock import patch, Mock

from core.models.pilas import Pilas
from core.forms.pila_form import PilasForm
from core.services.pilas_service import (
    get_pilas_paginated,
    create_pila,
    update_pila_stock_venta
)


class PilasModelTest(TestCase):
    """Tests esenciales para el modelo Pilas"""
    
    def test_pila_creation_with_defaults(self):
        """Test creación de pila con valores por defecto"""
        pila = Pilas.objects.create(codigo='TEST001', cantidad='10')
        
        self.assertEqual(pila.codigo, 'TEST001')
        self.assertEqual(pila.cantidad, '10')
        self.assertEqual(pila.precio, '0')  # Valor por defecto
        self.assertIsNotNone(pila.id)
    
    def test_pila_str_representation(self):
        """Test representación string del modelo"""
        pila = Pilas.objects.create(codigo='TEST001', precio='1500', cantidad='10')
        self.assertEqual(str(pila), "TEST001 - 1500 - 10")
    
    def test_codigo_unique_constraint(self):
        """Test restricción de código único"""
        Pilas.objects.create(codigo='TEST001', cantidad='10')
        
        with self.assertRaises(IntegrityError):
            Pilas.objects.create(codigo='TEST001', cantidad='5')


class PilasFormTest(TestCase):
    """Tests esenciales para PilasForm"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.existing_pila = Pilas.objects.create(
            codigo='EXISTING001',
            precio='1000',
            cantidad='5'
        )
    
    def test_form_fields_configuration(self):
        """Test configuración de campos del formulario"""
        form = PilasForm()
        
        self.assertEqual(form._meta.model, Pilas)
        self.assertEqual(set(form._meta.fields), {'codigo', 'cantidad'})
        # Verificar que precio NO está incluido
        self.assertNotIn('precio', form._meta.fields)
    
    def test_form_valid_data(self):
        """Test formulario con datos válidos"""
        form_data = {'codigo': 'FORM001', 'cantidad': '10'}
        form = PilasForm(data=form_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['codigo'], 'FORM001')
        self.assertEqual(form.cleaned_data['cantidad'], '10')
    
    def test_form_required_fields(self):
        """Test validación de campos requeridos"""
        # Sin código
        form = PilasForm(data={'cantidad': '5'})
        self.assertFalse(form.is_valid())
        self.assertIn('codigo', form.errors)
        
        # Sin cantidad
        form = PilasForm(data={'codigo': 'TEST001'})
        self.assertFalse(form.is_valid())
        self.assertIn('cantidad', form.errors)
    
    def test_codigo_unique_validation(self):
        """Test validación de código único"""
        # Modo creación con código duplicado
        form_data = {'codigo': 'EXISTING001', 'cantidad': '10'}
        form = PilasForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('codigo', form.errors)
        
        # Modo edición con mismo código (debe ser válido)
        form = PilasForm(data=form_data, instance=self.existing_pila)
        self.assertTrue(form.is_valid())
    
    def test_cantidad_validation(self):
        """Test validación de cantidad"""
        # Cantidad no numérica
        form = PilasForm(data={'codigo': 'TEST001', 'cantidad': 'abc'})
        self.assertFalse(form.is_valid())
        self.assertIn('cantidad', form.errors)
        
        # Cantidad con ceros a la izquierda (debe normalizarse)
        form = PilasForm(data={'codigo': 'TEST002', 'cantidad': '007'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['cantidad'], '7')
    
    def test_max_length_validation(self):
        """Test validación de longitud máxima"""
        # Código muy largo
        long_codigo = 'A' * 31
        form = PilasForm(data={'codigo': long_codigo, 'cantidad': '5'})
        self.assertFalse(form.is_valid())
        self.assertIn('codigo', form.errors)
        
        # Cantidad muy larga
        form = PilasForm(data={'codigo': 'TEST001', 'cantidad': '1234'})
        self.assertFalse(form.is_valid())
        self.assertIn('cantidad', form.errors)
    
    def test_form_save(self):
        """Test guardado del formulario"""
        form_data = {'codigo': 'SAVE001', 'cantidad': '15'}
        form = PilasForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        pila = form.save()
        self.assertEqual(pila.codigo, 'SAVE001')
        self.assertEqual(pila.cantidad, '15')
        self.assertEqual(pila.precio, '0')  # Precio por defecto


class PilasServiceTest(TestCase):
    """Tests esenciales para pilas_service"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear 10 pilas de prueba
        for i in range(10):
            Pilas.objects.create(
                codigo=f'SRV{i:03d}',
                precio=f'{1000 + i}',
                cantidad=str(i + 1)
            )
    
    def test_get_pilas_paginated_default(self):
        """Test paginación con parámetros por defecto"""
        page = get_pilas_paginated()
        
        self.assertEqual(page.number, 1)
        self.assertEqual(len(page.object_list), 6)  # items_per_page default
        self.assertTrue(page.has_next())
    
    def test_get_pilas_paginated_ordering(self):
        """Test ordenamiento correcto por código"""
        page = get_pilas_paginated()
        codigos = [pila.codigo for pila in page.object_list]
        self.assertEqual(codigos, sorted(codigos))
    
    def test_create_pila_new_instance(self):
        """Test creación de nueva pila"""
        form_data = {'codigo': 'NEW001', 'cantidad': '25'}
        form = PilasForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        pila = create_pila(form)
        
        self.assertEqual(pila.codigo, 'NEW001')
        self.assertEqual(pila.cantidad, '25')
        self.assertTrue(Pilas.objects.filter(codigo='NEW001').exists())
    
    def test_create_pila_edit_existing(self):
        """Test edición de pila existente"""
        existing_pila = Pilas.objects.create(codigo='EDIT001', precio='1500', cantidad='10')
        
        form_data = {'codigo': 'EDIT001', 'cantidad': '30'}
        form = PilasForm(data=form_data, instance=existing_pila)
        self.assertTrue(form.is_valid())
        
        updated_pila = create_pila(form)
        
        self.assertEqual(updated_pila.id, existing_pila.id)
        self.assertEqual(updated_pila.cantidad, '30')
        self.assertEqual(updated_pila.precio, '1500')  # Precio se mantiene
    
    def test_create_pila_exception_handling(self):
        """Test manejo de excepciones en create_pila"""
        mock_form = Mock()
        mock_form.save.side_effect = Exception("Error de base de datos")
        
        with self.assertRaises(Exception) as context:
            create_pila(mock_form)
        
        self.assertIn("Error al guardar la pila", str(context.exception))
    
    def test_update_pila_stock_venta(self):
        """Test actualización de stock en venta"""
        pila = Pilas.objects.create(codigo='STOCK001', precio='1000', cantidad='20')
        
        # Test con cantidad como string
        updated_pila = update_pila_stock_venta(pila.id, '5')
        self.assertEqual(updated_pila.cantidad, '15')
        
        # Test con cantidad como entero
        updated_pila = update_pila_stock_venta(pila.id, 3)
        self.assertEqual(updated_pila.cantidad, '12')
        
        # Verificar persistencia
        pila.refresh_from_db()
        self.assertEqual(pila.cantidad, '12')
    
    def test_update_pila_stock_nonexistent(self):
        """Test actualización de stock de pila inexistente"""
        with self.assertRaises(Pilas.DoesNotExist):
            update_pila_stock_venta(99999, 5)


class PilasViewTest(TestCase):
    """Tests esenciales para las vistas de Pilas"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = Client()
        
        self.list_url = reverse('pilas_list')
        self.create_url = reverse('pilas_form')
        
        self.test_pila = Pilas.objects.create(codigo='VIEW001', precio='1500', cantidad='15')
    
    def test_pilas_list_view_authenticated(self):
        """Test vista de lista con usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pilas/pilas_list.html')
        self.assertIn('pilas', response.context)
    
    def test_pilas_list_view_unauthenticated(self):
        """Test vista de lista sin autenticación"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_pila_create_view_get(self):
        """Test vista de creación con GET"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(self.create_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pilas/pila_form.html')
        self.assertEqual(response.context['modo'], 'agregar')
        self.assertIsInstance(response.context['form'], PilasForm)
    
    def test_pila_edit_view_get(self):
        """Test vista de edición con GET"""
        self.client.login(username='testuser', password='testpass123')
        
        edit_url = reverse('pila_editar', kwargs={'id': self.test_pila.id})
        response = self.client.get(edit_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['modo'], 'editar')
        self.assertEqual(response.context['form'].instance, self.test_pila)
    
    def test_pila_create_post_success(self):
        """Test creación exitosa de pila vía POST"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {'codigo': 'CREATE001', 'cantidad': '20'}
        response = self.client.post(self.create_url, data)
        
        self.assertRedirects(response, self.list_url)
        self.assertTrue(Pilas.objects.filter(codigo='CREATE001').exists())
        
        # Verificar mensaje
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Referencia de pila agregada con éxito')
    
    def test_pila_edit_post_success(self):
        """Test edición exitosa de pila vía POST"""
        self.client.login(username='testuser', password='testpass123')
        
        edit_url = reverse('pila_editar', kwargs={'id': self.test_pila.id})
        data = {'codigo': 'VIEW001', 'cantidad': '25'}
        response = self.client.post(edit_url, data)
        
        self.assertRedirects(response, self.list_url)
        
        self.test_pila.refresh_from_db()
        self.assertEqual(self.test_pila.cantidad, '25')
        
        # Verificar mensaje
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Referencia de pila editada con exito.')
    
    def test_pila_create_post_invalid(self):
        """Test POST con formulario inválido"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {'codigo': '', 'cantidad': 'abc'}
        response = self.client.post(self.create_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        
        # Verificar mensaje de error
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Error al procesar el formulario' in str(msg) for msg in messages))
    
    def test_view_unauthenticated_access(self):
        """Test acceso sin autenticación"""
        # Vista de creación
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)
        
        # Vista de edición
        edit_url = reverse('pila_editar', kwargs={'id': self.test_pila.id})
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 302)
    
    @patch('core.views.Pilas.pilas_view.create_pila')
    def test_pila_create_service_exception(self, mock_create_pila):
        """Test manejo de excepciones del servicio"""
        self.client.login(username='testuser', password='testpass123')
        mock_create_pila.side_effect = Exception("Error del servicio")
        
        data = {'codigo': 'ERROR001', 'cantidad': '10'}
        response = self.client.post(self.create_url, data)
        
        # Cuando ocurre excepción, la vista renderiza el formulario con el mensaje de error
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pilas/pila_form.html')
        
        # Verificar mensaje de error específico con el mensaje de la excepción
        messages = list(get_messages(response.wsgi_request))
        error_messages = [str(msg) for msg in messages]
        self.assertTrue(any('Error al guardar la pila: Error del servicio' in msg for msg in error_messages))
        
        # Verificar que el formulario tiene los datos enviados
        self.assertEqual(response.context['form']['codigo'].value(), 'ERROR001')
        self.assertEqual(response.context['form']['cantidad'].value(), '10')


class PilasIntegrationTest(TestCase):
    """Tests de integración para flujo completo de Pilas"""
    
    def setUp(self):
        """Configuración inicial para tests de integración"""
        self.user = User.objects.create_user(username='integrationuser', password='testpass123')
        self.client = Client()
        self.client.login(username='integrationuser', password='testpass123')
    
    def test_complete_pila_lifecycle(self):
        """Test del ciclo completo de vida de una pila"""
        # 1. Crear pila
        create_data = {'codigo': 'LIFECYCLE001', 'cantidad': '50'}
        response = self.client.post(reverse('pilas_form'), create_data)
        self.assertRedirects(response, reverse('pilas_list'))
        
        pila = Pilas.objects.get(codigo='LIFECYCLE001')
        self.assertEqual(pila.cantidad, '50')
        self.assertEqual(pila.precio, '0')
        
        # 2. Editar pila
        edit_data = {'codigo': 'LIFECYCLE001', 'cantidad': '75'}
        edit_url = reverse('pila_editar', kwargs={'id': pila.id})
        response = self.client.post(edit_url, edit_data)
        self.assertRedirects(response, reverse('pilas_list'))
        
        pila.refresh_from_db()
        self.assertEqual(pila.cantidad, '75')
        
        # 3. Simular venta
        updated_pila = update_pila_stock_venta(pila.id, 25)
        self.assertEqual(updated_pila.cantidad, '50')
        
        # 4. Verificar en lista
        response = self.client.get(reverse('pilas_list'))
        self.assertContains(response, 'LIFECYCLE001')
    
    def test_form_validation_integration(self):
        """Test integración de validaciones del formulario"""
        test_cases = [
            ({'codigo': 'VALID001', 'cantidad': '10'}, True),
            ({'codigo': '', 'cantidad': '10'}, False),
            ({'codigo': 'VALID002', 'cantidad': 'abc'}, False),
        ]
        
        for data, should_be_valid in test_cases:
            with self.subTest(data=data):
                response = self.client.post(reverse('pilas_form'), data)
                
                if should_be_valid:
                    self.assertRedirects(response, reverse('pilas_list'))
                else:
                    self.assertEqual(response.status_code, 200)
                    self.assertFalse(response.context['form'].is_valid())
