from django.test import TestCase
from core.forms.ganancia_form import ReporteGananciaForm, ReporteEgresoForm
from core.services.ganancia_service import (
    calcular_ganancia_rango, 
    obtener_ganancia_hoy,
    generar_pdf_ganancias
)
from core.models.ingreso import Ingreso
from core.models.egreso import Egreso
from datetime import date, timedelta
from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.views.Ganancia.ganancia_view import ganancia_view, reporte_ganancias_pdf
from unittest.mock import patch, Mock
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
    
    def test_form_fecha_inicio_invalida(self):
        """Prueba que el formulario maneja fechas de inicio inválidas"""
        form_data = {
            'inicio': 'fecha-invalida',
            'fin': self.hoy
        }
        form = ReporteGananciaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('inicio', form.errors)
        self.assertIn('Ingrese una fecha válida', str(form.errors['inicio']))
    
    def test_form_fecha_fin_invalida(self):
        """Prueba que el formulario maneja fechas de fin inválidas"""
        form_data = {
            'inicio': self.ayer,
            'fin': 'fecha-invalida'
        }
        form = ReporteGananciaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('fin', form.errors)
        self.assertIn('Ingrese una fecha válida', str(form.errors['fin']))
    
    def test_form_widget_attributes(self):
        """Prueba que los widgets tienen los atributos correctos"""
        from django import forms
        form = ReporteGananciaForm()
        
        # Verificar atributos del campo inicio
        inicio_widget = form.fields['inicio'].widget
        self.assertIsInstance(inicio_widget, forms.DateInput)
        self.assertEqual(inicio_widget.input_type, 'date')
        self.assertEqual(inicio_widget.attrs.get('id'), 'id_fecha_inicio')
        self.assertIn('form-control', inicio_widget.attrs.get('class', ''))
        
        # Verificar atributos del campo fin
        fin_widget = form.fields['fin'].widget
        self.assertIsInstance(fin_widget, forms.DateInput)
        self.assertEqual(fin_widget.input_type, 'date')
        self.assertEqual(fin_widget.attrs.get('id'), 'id_fecha_fin')
        self.assertIn('form-control', fin_widget.attrs.get('class', ''))
    
    def test_form_init_con_errores(self):
        """Prueba que el __init__ maneja correctamente los errores"""
        form_data = {
            'inicio': 'fecha-invalida',
            'fin': 'fecha-invalida'
        }
        form = ReporteGananciaForm(data=form_data)
        form.is_valid()  # Esto debe generar errores
        
        # Crear una nueva instancia para probar el __init__ con errores
        form_con_errores = ReporteGananciaForm(data=form_data)
        form_con_errores.full_clean()
        
        # Verificar que se aplican las clases de error
        self.assertIn('is-invalid', form_con_errores.fields['inicio'].widget.attrs.get('class', ''))
    
    def test_form_clean_method_mensaje_error(self):
        """Prueba que el método clean devuelve el mensaje de error correcto"""
        form_data = {
            'inicio': self.hoy,
            'fin': self.ayer
        }
        form = ReporteGananciaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('La fecha de inicio no puede ser posterior a la fecha de fin', str(form.errors))
    

class ReporteEgresoFormTest(TestCase):
    """Tests para el formulario ReporteEgresoForm (legacy)"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.hoy = date.today()
        self.ayer = self.hoy - timedelta(days=1)
    
    def test_form_valid(self):
        """Prueba que el formulario de egresos es válido con datos correctos"""
        form_data = {
            'inicio': self.ayer,
            'fin': self.hoy
        }
        form = ReporteEgresoForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_fecha_inicio_posterior(self):
        """Prueba que el formulario de egresos no es válido cuando fecha inicio > fecha fin"""
        form_data = {
            'inicio': self.hoy,
            'fin': self.ayer
        }
        form = ReporteEgresoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_form_campos_requeridos(self):
        """Prueba que los campos del formulario de egresos son requeridos"""
        form = ReporteEgresoForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('inicio', form.errors)
        self.assertIn('fin', form.errors)
    
    def test_form_widget_attributes(self):
        """Prueba que los widgets del formulario de egresos tienen los atributos correctos"""
        from django import forms
        form = ReporteEgresoForm()
        
        # Verificar atributos del campo inicio
        inicio_widget = form.fields['inicio'].widget
        self.assertIsInstance(inicio_widget, forms.DateInput)
        self.assertEqual(inicio_widget.input_type, 'date')
        self.assertEqual(inicio_widget.attrs.get('id'), 'id_fecha_inicio')
        self.assertIn('form-control', inicio_widget.attrs.get('class', ''))
        
        # Verificar atributos del campo fin
        fin_widget = form.fields['fin'].widget
        self.assertIsInstance(fin_widget, forms.DateInput)
        self.assertEqual(fin_widget.input_type, 'date')
        self.assertEqual(fin_widget.attrs.get('id'), 'id_fecha_fin')
        self.assertIn('form-control', fin_widget.attrs.get('class', ''))
    
    def test_form_init_con_errores(self):
        """Prueba que el __init__ del formulario de egresos maneja correctamente los errores"""
        form_data = {
            'inicio': 'fecha-invalida',
            'fin': self.hoy
        }
        form = ReporteEgresoForm(data=form_data)
        form.is_valid()  # Esto debe generar errores
        
        # Verificar que se aplican las clases de error
        self.assertIn('is-invalid', form.fields['inicio'].widget.attrs.get('class', ''))


class GananciaServiceTest(TestCase):
    """Tests para el servicio de ganancias"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.hoy = date.today()
        self.ayer = self.hoy - timedelta(days=1)
        self.hace_una_semana = self.hoy - timedelta(days=7)
        
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
    
    def test_calcular_ganancia_rango_con_perdidas(self):
        """Prueba el cálculo de ganancia cuando hay pérdidas (egresos > ingresos)"""
        # Crear un egreso mayor a los ingresos
        Egreso.objects.create(
            fecha=self.hoy,
            valor=500000,
            descripcion='Egreso grande'
        )
        
        resultado = calcular_ganancia_rango(self.hoy, self.hoy)
        
        # Total egresos: 50000 + 500000 = 550000
        # Total ingresos: 150000
        # Ganancia: 150000 - 550000 = -400000
        self.assertEqual(resultado['total_ingresos'], 150000)
        self.assertEqual(resultado['total_egresos'], 550000)
        self.assertEqual(resultado['ganancia_neta'], -400000)
    
    def test_calcular_ganancia_rango_solo_ingresos(self):
        """Prueba el cálculo de ganancia cuando solo hay ingresos"""
        # Eliminar todos los egresos
        Egreso.objects.all().delete()
        
        resultado = calcular_ganancia_rango(self.ayer, self.hoy)
        
        self.assertEqual(resultado['total_ingresos'], 350000)  # 150000 + 200000
        self.assertEqual(resultado['total_egresos'], 0)
        self.assertEqual(resultado['ganancia_neta'], 350000)
    
    def test_calcular_ganancia_rango_solo_egresos(self):
        """Prueba el cálculo de ganancia cuando solo hay egresos"""
        # Eliminar todos los ingresos
        Ingreso.objects.all().delete()
        
        resultado = calcular_ganancia_rango(self.hoy, self.hoy)
        
        self.assertEqual(resultado['total_ingresos'], 0)
        self.assertEqual(resultado['total_egresos'], 50000)
        self.assertEqual(resultado['ganancia_neta'], -50000)
    
    def test_calcular_ganancia_rango_fechas_iguales(self):
        """Prueba el cálculo de ganancia para un solo día"""
        resultado = calcular_ganancia_rango(self.hoy, self.hoy)
        
        self.assertEqual(resultado['total_ingresos'], 150000)
        self.assertEqual(resultado['total_egresos'], 50000)
        self.assertEqual(resultado['ganancia_neta'], 100000)
        self.assertEqual(resultado['fecha_inicio'], self.hoy)
        self.assertEqual(resultado['fecha_fin'], self.hoy)
    
    def test_calcular_ganancia_rango_periodo_largo(self):
        """Prueba el cálculo de ganancia para un período largo"""
        # Agregar más datos en diferentes fechas
        hace_dos_dias = self.hoy - timedelta(days=2)
        hace_tres_dias = self.hoy - timedelta(days=3)
        
        Ingreso.objects.create(
            fecha=hace_dos_dias,
            valor=100000,
            descripcion='Ingreso hace dos días'
        )
        
        Egreso.objects.create(
            fecha=hace_tres_dias,
            valor=25000,
            descripcion='Egreso hace tres días'
        )
        
        resultado = calcular_ganancia_rango(hace_tres_dias, self.hoy)
        
        # Total ingresos: 150000 + 200000 + 100000 = 450000
        # Total egresos: 50000 + 25000 = 75000
        # Ganancia: 450000 - 75000 = 375000
        self.assertEqual(resultado['total_ingresos'], 450000)
        self.assertEqual(resultado['total_egresos'], 75000)
        self.assertEqual(resultado['ganancia_neta'], 375000)
    
    @patch('core.services.ganancia_service.obtener_total_ingresos_rango')
    def test_calcular_ganancia_rango_error_ingresos(self, mock_ingresos):
        """Prueba el manejo de errores en obtener_total_ingresos_rango"""
        mock_ingresos.side_effect = Exception("Error al obtener ingresos")
        
        with self.assertRaises(Exception) as context:
            calcular_ganancia_rango(self.ayer, self.hoy)
        
        self.assertIn("Error al calcular ganancia", str(context.exception))
        self.assertIn("Error al obtener ingresos", str(context.exception))
    
    @patch('core.services.ganancia_service.obtener_total_egresos_rango')
    def test_calcular_ganancia_rango_error_egresos(self, mock_egresos):
        """Prueba el manejo de errores en obtener_total_egresos_rango"""
        mock_egresos.side_effect = Exception("Error al obtener egresos")
        
        with self.assertRaises(Exception) as context:
            calcular_ganancia_rango(self.ayer, self.hoy)
        
        self.assertIn("Error al calcular ganancia", str(context.exception))
        self.assertIn("Error al obtener egresos", str(context.exception))
    
    def test_obtener_ganancia_hoy_sin_datos(self):
        """Prueba obtener ganancia de hoy cuando no hay datos"""
        # Eliminar todos los datos
        Ingreso.objects.all().delete()
        Egreso.objects.all().delete()
        
        resultado = obtener_ganancia_hoy()
        
        self.assertEqual(resultado['total_ingresos'], 0)
        self.assertEqual(resultado['total_egresos'], 0)
        self.assertEqual(resultado['ganancia_neta'], 0)
        self.assertEqual(resultado['fecha_inicio'], self.hoy)
        self.assertEqual(resultado['fecha_fin'], self.hoy)


class GananciaServicePDFTest(TestCase):
    """Tests para la generación de PDF del servicio de ganancias"""
    
    def setUp(self):
        """Configuración inicial para las pruebas de PDF"""
        self.hoy = date.today()
        self.ayer = self.hoy - timedelta(days=1)
        
        # Crear datos de prueba
        Ingreso.objects.create(
            fecha=self.hoy,
            valor=150000,
            descripcion='Ingreso de prueba'
        )
        
        Egreso.objects.create(
            fecha=self.hoy,
            valor=50000,
            descripcion='Egreso de prueba'
        )
    
    def test_generar_pdf_ganancias_basico(self):
        """Prueba la generación básica de PDF de ganancias"""
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/test/')
        
        datos_ganancia = {
            'total_ingresos': 150000,
            'total_egresos': 50000,
            'ganancia_neta': 100000
        }
        
        pdf_content = generar_pdf_ganancias(self.ayer, self.hoy, datos_ganancia, request)
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))
    
    def test_generar_pdf_ganancias_con_perdidas(self):
        """Prueba la generación de PDF cuando hay pérdidas"""
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/test/')
        
        datos_ganancia = {
            'total_ingresos': 50000,
            'total_egresos': 150000,
            'ganancia_neta': -100000  # Pérdida
        }
        
        pdf_content = generar_pdf_ganancias(self.ayer, self.hoy, datos_ganancia, request)
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))
    
    def test_generar_pdf_ganancias_sin_datos(self):
        """Prueba la generación de PDF cuando no hay datos"""
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/test/')
        
        datos_ganancia = {
            'total_ingresos': 0,
            'total_egresos': 0,
            'ganancia_neta': 0
        }
        
        pdf_content = generar_pdf_ganancias(self.ayer, self.hoy, datos_ganancia, request)
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))
    
    @patch('django.contrib.staticfiles.finders.find')
    @patch('reportlab.platypus.Image')
    def test_generar_pdf_ganancias_con_logo(self, mock_image_class, mock_find):
        """Prueba la generación de PDF cuando se encuentra el logo"""
        from django.test import RequestFactory
        
        # Mock para simular que se encuentra el logo
        mock_find.return_value = '/path/to/logo.png'
        
        # Mock de la clase Image para que devuelva un objeto compatible
        mock_image_instance = Mock()
        mock_image_instance.getKeepWithNext.return_value = False
        mock_image_instance.wrap.return_value = (100, 50)
        mock_image_instance.drawOn = Mock()
        mock_image_class.return_value = mock_image_instance
        
        factory = RequestFactory()
        request = factory.get('/test/')
        
        datos_ganancia = {
            'total_ingresos': 150000,
            'total_egresos': 50000,
            'ganancia_neta': 100000
        }
        
        pdf_content = generar_pdf_ganancias(self.ayer, self.hoy, datos_ganancia, request)
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))
        
        # Verificar que se intentó usar el logo
        mock_image_class.assert_called_once()
    
    @patch('django.contrib.staticfiles.finders.find')
    def test_generar_pdf_ganancias_sin_logo(self, mock_find):
        """Prueba la generación de PDF cuando no se encuentra el logo"""
        from django.test import RequestFactory
        
        # Mock para simular que no se encuentra el logo
        mock_find.return_value = None
        
        factory = RequestFactory()
        request = factory.get('/test/')
        
        datos_ganancia = {
            'total_ingresos': 150000,
            'total_egresos': 50000,
            'ganancia_neta': 100000
        }
        
        pdf_content = generar_pdf_ganancias(self.ayer, self.hoy, datos_ganancia, request)
        
        # Verificar que se generó contenido PDF sin errores
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))
    
    @patch('django.contrib.staticfiles.finders.find')
    def test_generar_pdf_ganancias_error_logo(self, mock_find):
        """Prueba la generación de PDF cuando hay error con el logo"""
        from django.test import RequestFactory
        
        # Mock para simular error al buscar el logo
        mock_find.side_effect = Exception("Error al buscar logo")
        
        factory = RequestFactory()
        request = factory.get('/test/')
        
        datos_ganancia = {
            'total_ingresos': 150000,
            'total_egresos': 50000,
            'ganancia_neta': 100000
        }
        
        # Debería manejar el error gracefully
        pdf_content = generar_pdf_ganancias(self.ayer, self.hoy, datos_ganancia, request)
        
        # Verificar que se generó contenido PDF sin errores
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))
    
    @patch('core.services.ganancia_service.timezone')
    def test_generar_pdf_ganancias_fecha_footer(self, mock_timezone):
        """Prueba que se incluye la fecha en el footer del PDF"""
        from django.test import RequestFactory
        from datetime import datetime
        
        # Mock para controlar la fecha
        mock_now = datetime(2024, 6, 15, 14, 30, 0)
        mock_timezone.now.return_value = mock_now
        
        factory = RequestFactory()
        request = factory.get('/test/')
        
        datos_ganancia = {
            'total_ingresos': 150000,
            'total_egresos': 50000,
            'ganancia_neta': 100000
        }
        
        pdf_content = generar_pdf_ganancias(self.ayer, self.hoy, datos_ganancia, request)
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))
        
        # Verificar que se llamó timezone.now para la fecha
        mock_timezone.now.assert_called()
    
    def test_generar_pdf_ganancias_sin_request(self):
        """Prueba la generación de PDF sin objeto request"""
        datos_ganancia = {
            'total_ingresos': 150000,
            'total_egresos': 50000,
            'ganancia_neta': 100000
        }
        
        pdf_content = generar_pdf_ganancias(self.ayer, self.hoy, datos_ganancia, None)
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))
    
    def test_generar_pdf_ganancias_datos_grandes(self):
        """Prueba la generación de PDF con números grandes"""
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/test/')
        
        datos_ganancia = {
            'total_ingresos': 1500000000,  # 1.5 mil millones
            'total_egresos': 500000000,    # 500 millones
            'ganancia_neta': 1000000000    # 1 mil millones
        }
        
        pdf_content = generar_pdf_ganancias(self.ayer, self.hoy, datos_ganancia, request)
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))
    
    @patch('reportlab.platypus.SimpleDocTemplate.build')
    def test_generar_pdf_ganancias_error_construccion(self, mock_build):
        """Prueba el manejo de errores durante la construcción del PDF"""
        from django.test import RequestFactory
        
        # Mock para simular error en la construcción del PDF
        mock_build.side_effect = Exception("Error al construir PDF")
        
        factory = RequestFactory()
        request = factory.get('/test/')
        
        datos_ganancia = {
            'total_ingresos': 150000,
            'total_egresos': 50000,
            'ganancia_neta': 100000
        }
        
        with self.assertRaises(Exception) as context:
            generar_pdf_ganancias(self.ayer, self.hoy, datos_ganancia, request)
        
        self.assertIn("Error al generar PDF", str(context.exception))
        self.assertIn("Error al construir PDF", str(context.exception))


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
    
    def test_ganancia_view_usuario_no_autenticado(self):
        """Prueba acceso sin autenticación"""
        self.client.logout()
        response = self.client.get(reverse('ganancia'))
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
    
    @patch('core.views.Ganancia.ganancia_view.obtener_ganancia_hoy')
    def test_ganancia_view_con_perdidas(self, mock_ganancia_hoy):
        """Prueba vista GET de ganancias con pérdidas"""
        mock_ganancia_hoy.return_value = {
            'ganancia_neta': -50000,  # Pérdida
            'total_ingresos': 100000,
            'total_egresos': 150000
        }
        
        response = self.client.get(reverse('ganancia'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['ganancia_data']['ganancia_neta'], -50000)
    
    def test_reporte_ganancias_pdf_solo_inicio(self):
        """Prueba PDF solo con fecha de inicio"""
        response = self.client.get(reverse('reporte_ganancias_pdf'), {
            'inicio': '2023-06-01'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'proporcionar el rango de fechas', response.content)
    
    def test_reporte_ganancias_pdf_solo_fin(self):
        """Prueba PDF solo con fecha de fin"""
        response = self.client.get(reverse('reporte_ganancias_pdf'), {
            'fin': '2023-06-30'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'proporcionar el rango de fechas', response.content)
    
    @patch('core.views.Ganancia.ganancia_view.generar_pdf_ganancias')
    @patch('core.views.Ganancia.ganancia_view.calcular_ganancia_rango')
    def test_reporte_ganancias_pdf_fechas_iguales(self, mock_calcular, mock_pdf):
        """Prueba generación de PDF con fechas iguales"""
        mock_calcular.return_value = {
            'total_ingresos': 50000,
            'total_egresos': 20000,
            'ganancia_neta': 30000
        }
        mock_pdf.return_value = b'PDF content'
        
        response = self.client.get(reverse('reporte_ganancias_pdf'), {
            'inicio': '2023-06-15',
            'fin': '2023-06-15'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
    
    @patch('core.views.Ganancia.ganancia_view.generar_pdf_ganancias')
    def test_reporte_ganancias_pdf_error_pdf(self, mock_pdf):
        """Prueba manejo de errores específicos en generación de PDF"""
        mock_pdf.side_effect = Exception("Error al generar PDF")
        
        response = self.client.get(reverse('reporte_ganancias_pdf'), {
            'inicio': '2023-06-01',
            'fin': '2023-06-30'
        })
        
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Error al generar el reporte', response.content)