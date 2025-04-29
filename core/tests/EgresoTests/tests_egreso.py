from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from core.models import Egreso
from core.forms import EgresoForm
import datetime
from unittest.mock import patch

class EgresoModelTest(TestCase):
    """
    Pruebas unitarias para el modelo Egreso
    """
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.egreso_data = {
            'valor': Decimal('1000.00'),
            'fecha': timezone.now().date(),
            'descripcion': 'Test descripción'
        }
        
    def test_crear_egreso(self):
        """Prueba la creación de un egreso válido"""
        egreso = Egreso.objects.create(**self.egreso_data)
        self.assertEqual(egreso.valor, self.egreso_data['valor'])
        self.assertEqual(egreso.fecha, self.egreso_data['fecha'])
        self.assertEqual(egreso.descripcion, self.egreso_data['descripcion'])
        
    def test_max_length_descripcion(self):
        descripcion_larga = 'a' * 111
        self.egreso_data['descripcion'] = descripcion_larga
        
        with self.assertRaises(Exception):  # Más específico que Exception
            egreso = Egreso(**self.egreso_data)
            egreso.full_clean()  # Forzar validación
            
    def test_max_digits_valor(self):
        valor_grande = Decimal('12345678901')  # 11 dígitos
        self.egreso_data['valor'] = valor_grande
        
        with self.assertRaises(Exception):  # Más específico que Exception
            egreso = Egreso(**self.egreso_data)
            egreso.full_clean()


class EgresoFormTest(TestCase):
    """
    Pruebas unitarias para el formulario EgresoForm
    """
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.form_data = {
            'valor': '1000',
            'fecha': '01/01/2025',  # Cambiado a formato dd/mm/yyyy
            'descripcion': 'Test descripción'
        }
        
    def test_form_valid(self):
        """Prueba que el formulario sea válido con datos correctos"""
        form = EgresoForm(data=self.form_data)
        self.assertTrue(form.is_valid())
        
    def test_form_invalid_campo_vacio(self):
        """Prueba que el formulario sea inválido cuando faltan campos"""
        # Prueba para cada campo requerido
        campos_requeridos = ['valor', 'fecha', 'descripcion']
        
        for campo in campos_requeridos:
            with self.subTest(campo=campo):
                # Copia los datos del formulario y elimina un campo
                data_incompleta = self.form_data
                data_incompleta.pop(campo)
                
                form = EgresoForm(data=data_incompleta)
                self.assertFalse(form.is_valid())
                self.assertIn(campo, form.errors)
                self.assertEqual(form.errors[campo][0], 'Campo incompleto')
    
    def test_form_invalid_valor_no_numerico(self):
        """Prueba que el formulario sea inválido cuando el valor no es numérico"""
        data_invalida = self.form_data.copy()
        data_invalida['valor'] = 'abc'
        
        form = EgresoForm(data=data_invalida)
        self.assertFalse(form.is_valid())
        self.assertIn('valor', form.errors)
        
    
        
    def test_clean_descripcion_max_length(self):
        """Prueba la validación personalizada para la longitud máxima de la descripción"""
        data_invalida = self.form_data.copy()
        data_invalida['descripcion'] = 'a' * 101  # Más de 100 caracteres
        
        form = EgresoForm(data=data_invalida)
        self.assertFalse(form.is_valid())
        self.assertIn('descripcion', form.errors)
        self.assertEqual(form.errors['descripcion'][0], "Máximo 100 caracteres permitidos")
        
    


class UsuarioCrearEgresoViewTest(TestCase):
    """
    Pruebas unitarias para la vista usuario_crear_egreso
    """
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.client = Client()
        self.url = reverse('egreso')  # Asegúrate de que este nombre coincida con tu URL
        self.form_data = {
            'valor': '1000',
            'fecha': '2025-01-01',
            'descripcion': 'Test descripción'
        }
        
    def test_get_request(self):
        """Prueba que la vista responda correctamente a una solicitud GET"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'egreso/egreso_form.html')
        self.assertIsInstance(response.context['form'], EgresoForm)

        
        
    def test_post_valid_data(self):
        """Prueba que la vista maneje correctamente datos POST válidos"""
        response = self.client.post(self.url, self.form_data)
        
        
        
        # Verifica que redirige a la página correcta
        self.assertRedirects(response, reverse('confirmar_egreso'))
        
    
    def test_post_invalid_data(self):
        """Prueba que la vista maneje correctamente datos POST inválidos"""
        # Datos inválidos: falta el campo valor
        data_invalida = self.form_data.copy()
        data_invalida.pop('valor')
        
        response = self.client.post(self.url, data_invalida)
        
        
        
        # Verifica que se muestra el formulario con errores
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'egreso/egreso_form.html')
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('valor', response.context['form'].errors)


