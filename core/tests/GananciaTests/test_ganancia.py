from django.test import TestCase
from core.forms.ganancia_form import ReporteGananciaForm
from core.services.ganancia_service import (
    calcular_ganancia_rango, 
    obtener_ganancia_hoy
)
from core.models.ingreso import Ingreso
from core.models.egreso import Egreso
from datetime import date, timedelta
from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.views.Ganancia.ganancia_view import ganancia_view, reporte_ganancias_pdf
from unittest.mock import patch
import json


class ReporteGananciaFormTest(TestCase):
    """Tests para el formulario ReporteGananciaForm"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.hoy = date.today()
        self.ayer = self.hoy - timedelta(days=1)
        
    def test_form_valid(self):
        """Prueba que el formulario es válido con datos correctos"""
        form_data = {
            'inicio': self.ayer,
            'fin': self.hoy
        }
        form = ReporteGananciaForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_fecha_inicio_posterior(self):
        """Prueba que el formulario no es válido cuando fecha inicio > fecha fin"""
        form_data = {
            'inicio': self.hoy,
            'fin': self.ayer
        }
        form = ReporteGananciaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_form_campos_requeridos(self):
        """Prueba que los campos son requeridos"""
        form = ReporteGananciaForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('inicio', form.errors)
        self.assertIn('fin', form.errors)
    
    def test_form_fechas_iguales(self):
        """Prueba que el formulario es válido con fechas iguales"""
        form_data = {
            'inicio': self.hoy,
            'fin': self.hoy
        }
        form = ReporteGananciaForm(data=form_data)
        self.assertTrue(form.is_valid())


class GananciaServiceTest(TestCase):
    """Tests para el servicio de ganancias"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.hoy = date.today()
        self.ayer = self.hoy - timedelta(days=1)
        
        # Crear datos de prueba
        self.ingreso_hoy = Ingreso.objects.create(
            fecha=self.hoy,
            valor=150000,
            descripcion='Ingreso de prueba hoy'
        )
        
        self.egreso_hoy = Egreso.objects.create(
            fecha=self.hoy,
            valor=50000,
            descripcion='Egreso de prueba hoy'
        )
        
        self.ingreso_ayer = Ingreso.objects.create(
            fecha=self.ayer,
            valor=200000,
            descripcion='Ingreso de prueba ayer'
        )
        
    def test_calcular_ganancia_rango(self):
        """Prueba el cálculo de ganancia en un rango de fechas"""
        resultado = calcular_ganancia_rango(self.ayer, self.hoy)
        
        self.assertEqual(resultado['total_ingresos'], 350000)  # 150000 + 200000
        self.assertEqual(resultado['total_egresos'], 50000)
        self.assertEqual(resultado['ganancia_neta'], 300000)  # 350000 - 50000
        self.assertEqual(resultado['fecha_inicio'], self.ayer)
        self.assertEqual(resultado['fecha_fin'], self.hoy)
    
    def test_obtener_ganancia_hoy(self):
        """Prueba obtener la ganancia del día actual"""
        resultado = obtener_ganancia_hoy()
        
        self.assertEqual(resultado['total_ingresos'], 150000)
        self.assertEqual(resultado['total_egresos'], 50000)
        self.assertEqual(resultado['ganancia_neta'], 100000)
        self.assertEqual(resultado['fecha_inicio'], self.hoy)
        self.assertEqual(resultado['fecha_fin'], self.hoy)
    
    def test_calcular_ganancia_sin_datos(self):
        """Prueba el cálculo de ganancia cuando no hay datos"""
        fecha_futura = self.hoy + timedelta(days=30)
        resultado = calcular_ganancia_rango(fecha_futura, fecha_futura)
        
        self.assertEqual(resultado['total_ingresos'], 0)
        self.assertEqual(resultado['total_egresos'], 0)
        self.assertEqual(resultado['ganancia_neta'], 0)


class GananciaViewTest(TestCase):
    """Tests para las vistas de ganancia"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    @patch('core.views.Ganancia.ganancia_view.obtener_ganancia_hoy')
    def test_ganancia_view_get(self, mock_ganancia_hoy):
        """Prueba vista GET de ganancias"""
        mock_ganancia_hoy.return_value = {
            'ganancia_neta': 100000,
            'total_ingresos': 150000,
            'total_egresos': 50000
        }
        
        response = self.client.get(reverse('ganancia'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ganancia/ganancia.html')
        self.assertIn('form', response.context)
        self.assertIn('ganancia_data', response.context)
    
    @patch('core.views.Ganancia.ganancia_view.obtener_ganancia_hoy')
    def test_ganancia_view_get_error(self, mock_ganancia_hoy):
        """Prueba vista GET de ganancias con error en el servicio"""
        mock_ganancia_hoy.side_effect = Exception("Error de prueba")
        
        response = self.client.get(reverse('ganancia'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['ganancia_data']['ganancia_neta'], 0)
    
    def test_reporte_ganancias_pdf_sin_parametros(self):
        """Prueba PDF sin parámetros de fecha"""
        response = self.client.get(reverse('reporte_ganancias_pdf'))
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'proporcionar el rango de fechas', response.content)
    
    def test_reporte_ganancias_pdf_fecha_invalida(self):
        """Prueba PDF con formato de fecha inválido"""
        response = self.client.get(reverse('reporte_ganancias_pdf'), {
            'inicio': 'fecha-invalida',
            'fin': '2023-06-30'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Formato de fecha', response.content)
    
    def test_reporte_ganancias_pdf_fecha_inicio_posterior(self):
        """Prueba PDF con fecha inicio posterior a fecha fin"""
        response = self.client.get(reverse('reporte_ganancias_pdf'), {
            'inicio': '2023-06-30',
            'fin': '2023-06-01'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'fecha de inicio no puede ser posterior', response.content)
    
    @patch('core.views.Ganancia.ganancia_view.generar_pdf_ganancias')
    @patch('core.views.Ganancia.ganancia_view.calcular_ganancia_rango')
    def test_reporte_ganancias_pdf_exitoso(self, mock_calcular, mock_pdf):
        """Prueba generación exitosa de PDF de ganancias"""
        mock_calcular.return_value = {
            'total_ingresos': 100000,
            'total_egresos': 30000,
            'ganancia_neta': 70000
        }
        mock_pdf.return_value = b'PDF content'
        
        response = self.client.get(reverse('reporte_ganancias_pdf'), {
            'inicio': '2023-06-01',
            'fin': '2023-06-30'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('filename=', response['Content-Disposition'])
    
    @patch('core.views.Ganancia.ganancia_view.calcular_ganancia_rango')
    def test_reporte_ganancias_pdf_error_interno(self, mock_calcular):
        """Prueba manejo de errores internos en generación de PDF"""
        mock_calcular.side_effect = Exception("Error interno")
        
        response = self.client.get(reverse('reporte_ganancias_pdf'), {
            'inicio': '2023-06-01',
            'fin': '2023-06-30'
        })
        
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Error al generar el reporte', response.content)