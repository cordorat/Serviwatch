from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from core.models.pilas import Pilas
from core.models.VentaPila import VentaPila
from core.services.pilas_service import update_pila_stock_venta
from core.views.Pilas.ventaPila_view import ventaPilas_list_view, ventaPila_view
from datetime import datetime
from django.contrib.messages import get_messages
import json

class TestPilasService(TestCase):
    """Pruebas para el servicio de pilas"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        # Crear una pila de prueba
        self.pila = Pilas.objects.create(
            codigo="AA123",
            precio="1000",
            cantidad="50"
        )
    
    def test_update_pila_stock_venta(self):
        """Probar decremento de stock"""
        pila_actualizada = update_pila_stock_venta(self.pila.id, "20")
        self.assertEqual(int(pila_actualizada.cantidad), 30)
        
        # Verificar que se guardó en la base de datos
        pila_db = Pilas.objects.get(id=self.pila.id)
        self.assertEqual(int(pila_db.cantidad), 30)


class TestVentaPilaView(TestCase):
    """Pruebas para las vistas de venta de pilas"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.client = Client()
        self.factory = RequestFactory()
        
        # Crear usuario para login
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )
        
        # Crear pilas de prueba
        self.pila1 = Pilas.objects.create(
            codigo="AA123",
            precio="1000",
            cantidad="50"
        )
        
        self.pila2 = Pilas.objects.create(
            codigo="BB456",
            precio="2000",
            cantidad="30"
        )
    
    def test_ventaPilas_list_view(self):
        """Probar vista de listado de pilas disponibles para venta"""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Hacer GET request
        response = self.client.get(reverse('ventaPila_list'))
        
        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pilas/ventaPila_list.html')
        self.assertIn('pilas', response.context)
        
        # Verificar que las pilas estén en el contexto
        pilas_in_context = list(response.context['pilas'])
        self.assertEqual(len(pilas_in_context), 2)
    
    def test_ventaPila_view_exito(self):
        """Probar registro de venta exitoso"""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Datos de venta
        post_data = {
            f'cantidad_{self.pila1.id}': '10',
            f'cantidad_{self.pila2.id}': '5'
        }
        
        # Hacer POST request
        response = self.client.post(reverse('ventaPila_create'), post_data)
        
        # Verificar redirección
        self.assertRedirects(response, reverse('ventaPila_list'))
        
        # Verificar mensaje de éxito
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Venta agregada correctamente.')
        
        # Verificar que se actualizó el stock
        pila1_actualizada = Pilas.objects.get(id=self.pila1.id)
        pila2_actualizada = Pilas.objects.get(id=self.pila2.id)
        self.assertEqual(int(pila1_actualizada.cantidad), 40)
        self.assertEqual(int(pila2_actualizada.cantidad), 25)
        
        # Verificar que se crearon los registros de venta
        ventas_pila1 = VentaPila.objects.filter(pila=self.pila1)
        ventas_pila2 = VentaPila.objects.filter(pila=self.pila2)
        self.assertEqual(ventas_pila1.count(), 1)
        self.assertEqual(ventas_pila2.count(), 1)
        self.assertEqual(ventas_pila1.first().cantidad, 10)
        self.assertEqual(ventas_pila2.first().cantidad, 5)
    
    def test_ventaPila_view_sin_seleccion(self):
        """Probar intento de venta sin seleccionar pilas"""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Datos de venta vacíos
        post_data = {
            f'cantidad_{self.pila1.id}': '0',
            f'cantidad_{self.pila2.id}': '0'
        }
        
        # Hacer POST request
        response = self.client.post(reverse('ventaPila_create'), post_data)
        
        # Verificar redirección
        self.assertRedirects(response, reverse('ventaPila_list'))
        
        # Verificar mensaje de error
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'No se han seleccionado pilas para la venta.')
    
    def test_ventaPila_view_stock_insuficiente(self):
        """Probar intento de venta con stock insuficiente"""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Datos de venta con cantidad mayor al stock disponible
        post_data = {
            f'cantidad_{self.pila1.id}': '60',  # Stock es 50
        }
        
        # Hacer POST request
        response = self.client.post(reverse('ventaPila_create'), post_data)
        
        # Verificar redirección
        self.assertRedirects(response, reverse('ventaPila_list'))
        
        # Verificar mensaje de error
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'Stock insuficiente para la pila {self.pila1.codigo}.')
        
        # Verificar que no se actualizó el stock
        pila1_actualizada = Pilas.objects.get(id=self.pila1.id)
        self.assertEqual(pila1_actualizada.cantidad, '50')
        
        # Verificar que no se crearon registros de venta
        ventas = VentaPila.objects.all()
        self.assertEqual(ventas.count(), 0)