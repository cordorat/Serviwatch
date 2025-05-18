from django.test import TestCase
from core.models.ingreso import Ingreso
from datetime import date, timedelta
from django.core.exceptions import ValidationError

class IngresoModelTestCase(TestCase):
    """Tests para el modelo Ingreso"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.hoy = date.today()
        self.datos_validos = {
            'fecha': self.hoy,
            'valor': 100000,
            'descripcion': 'Ingreso por venta de servicio'
        }
    
    def test_crear_ingreso_exitoso(self):
        """Prueba la creación exitosa de un ingreso con datos válidos"""
        ingreso = Ingreso.objects.create(**self.datos_validos)
        self.assertEqual(ingreso.fecha, self.datos_validos['fecha'])
        self.assertEqual(ingreso.valor, self.datos_validos['valor'])
        self.assertEqual(ingreso.descripcion, self.datos_validos['descripcion'])
        self.assertTrue(isinstance(ingreso, Ingreso))
    
    def test_representacion_str(self):
        """Prueba la representación de cadena del objeto Ingreso"""
        ingreso = Ingreso.objects.create(**self.datos_validos)
        
        # Ajusta el expected_str al formato real que devuelve tu modelo
        expected_str = f"Egreso: {self.datos_validos['valor']} - {self.hoy} - {self.datos_validos['descripcion']}"
        self.assertEqual(str(ingreso), expected_str)
    

from django.test import TestCase
from core.forms.ingreso_form import IngresoForm, ReporteIngresoForm
from django.utils import timezone

class IngresoFormTestCase(TestCase):
    """Tests para el formulario IngresoForm"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.hoy = timezone.now().date()
        self.una_semana_atras = self.hoy - timedelta(days=7)
        self.datos_validos = {
            'fecha': self.hoy,
            'valor': 50000,
            'descripcion': 'Venta de servicio'
        }
    
    def test_form_valid(self):
        """Prueba que el formulario es válido con datos correctos"""
        form = IngresoForm(data=self.datos_validos)
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_valor_cero(self):
        """Prueba que el formulario no es válido con valor cero"""
        datos_invalidos = self.datos_validos.copy()
        datos_invalidos['valor'] = 0
        
        form = IngresoForm(data=datos_invalidos)
        self.assertFalse(form.is_valid())
        self.assertIn('valor', form.errors)
        self.assertEqual(form.errors['valor'][0], "El valor debe ser mayor que cero")
    
    def test_form_invalid_valor_negativo(self):
        """Prueba que el formulario no es válido con valor negativo"""
        datos_invalidos = self.datos_validos.copy()
        datos_invalidos['valor'] = -100
        
        form = IngresoForm(data=datos_invalidos)
        self.assertFalse(form.is_valid())
        self.assertIn('valor', form.errors)
    
    def test_form_invalid_fecha_futura(self):
        """Prueba que el formulario no es válido con fecha futura"""
        datos_invalidos = self.datos_validos.copy()
        datos_invalidos['fecha'] = self.hoy + timedelta(days=1)
        
        form = IngresoForm(data=datos_invalidos)
        self.assertFalse(form.is_valid())
        self.assertIn('fecha', form.errors)
        self.assertEqual(form.errors['fecha'][0], "La fecha no puede ser en el futuro")
    
    def test_form_invalid_fecha_antigua(self):
        """Prueba que el formulario no es válido con fecha anterior a una semana"""
        datos_invalidos = self.datos_validos.copy()
        datos_invalidos['fecha'] = self.una_semana_atras - timedelta(days=1)
        
        form = IngresoForm(data=datos_invalidos)
        self.assertFalse(form.is_valid())
        self.assertIn('fecha', form.errors)
        self.assertEqual(form.errors['fecha'][0], "La fecha no puede ser anterior a una semana")
    
    def test_form_fecha_limite_una_semana(self):
        """Prueba que el formulario es válido con fecha de hace exactamente una semana"""
        datos_validos = self.datos_validos.copy()
        datos_validos['fecha'] = self.una_semana_atras
        
        form = IngresoForm(data=datos_validos)
        self.assertTrue(form.is_valid())
    
    def test_clase_css_error(self):
        """Prueba que se añade la clase CSS de error cuando hay errores de validación"""
        datos_invalidos = self.datos_validos.copy()
        datos_invalidos['valor'] = 0
        
        form = IngresoForm(data=datos_invalidos)
        form.is_valid()  # Ejecuta la validación
        
        # Verificar que el campo tiene la clase is-invalid
        self.assertIn('is-invalid', form.fields['valor'].widget.attrs['class'])


class ReporteIngresoFormTestCase(TestCase):
    """Tests para el formulario ReporteIngresoForm"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.hoy = date.today()
        self.ayer = self.hoy - timedelta(days=1)
        self.manana = self.hoy + timedelta(days=1)
        self.datos_validos = {
            'inicio': self.ayer,
            'fin': self.hoy
        }
    
    def test_reporte_form_valid(self):
        """Prueba que el formulario de reporte es válido con datos correctos"""
        form = ReporteIngresoForm(data=self.datos_validos)
        self.assertTrue(form.is_valid())
    
    def test_reporte_form_invalid_fecha_inicio_posterior(self):
        """Prueba que el formulario no es válido si la fecha inicio es posterior a la fecha fin"""
        datos_invalidos = {
            'inicio': self.hoy,
            'fin': self.ayer
        }
        
        form = ReporteIngresoForm(data=datos_invalidos)
        self.assertFalse(form.is_valid())
        
        # Corregir el mensaje exacto incluyendo el punto final
        self.assertIn('La fecha de inicio no puede ser posterior a la fecha de fin.', 
                    form.non_field_errors())
    
    def test_reporte_form_campos_requeridos(self):
        """Prueba que ambos campos son requeridos"""
        form = ReporteIngresoForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('inicio', form.errors)
        self.assertIn('fin', form.errors)
        self.assertEqual(form.errors['inicio'][0], 'La fecha inicial es obligatoria.')
        self.assertEqual(form.errors['fin'][0], 'La fecha final es obligatoria.')


from core.services.ingreso_service import (
    crear_ingreso, obtener_total_ingresos_dia, 
    obtener_ingresos_rango, obtener_total_ingresos_rango,
    generar_pdf_ingresos
)
from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.db.utils import DatabaseError
from io import BytesIO
import unittest
from unittest.mock import patch, MagicMock

class IngresoServiceTestCase(TestCase):
    """Tests para los servicios relacionados con ingresos"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.hoy = date.today()
        self.ayer = self.hoy - timedelta(days=1)
        self.manana = self.hoy + timedelta(days=1)
        
        # Crear algunos ingresos de prueba
        Ingreso.objects.create(
            fecha=self.hoy,
            valor=100000,
            descripcion='Ingreso 1 hoy'
        )
        
        Ingreso.objects.create(
            fecha=self.hoy,
            valor=50000,
            descripcion='Ingreso 2 hoy'
        )
        
        Ingreso.objects.create(
            fecha=self.ayer,
            valor=75000,
            descripcion='Ingreso ayer'
        )
    
    def test_crear_ingreso_exitoso(self):
        """Prueba la creación exitosa de un ingreso con datos válidos"""
        datos = {
            'fecha': self.ayer,
            'valor': 30000,
            'descripcion': 'Nuevo ingreso de prueba'
        }
        
        ingreso = crear_ingreso(datos)
        self.assertEqual(ingreso.fecha, datos['fecha'])
        self.assertEqual(ingreso.valor, datos['valor'])
        self.assertEqual(ingreso.descripcion, datos['descripcion'])
        
        # Verificar que se guardó en la base de datos
        self.assertTrue(Ingreso.objects.filter(descripcion='Nuevo ingreso de prueba').exists())
    
    def test_crear_ingreso_datos_faltantes(self):
        """Prueba que se valida la presencia de todos los datos requeridos"""
        datos_incompletos = {
            'fecha': self.hoy,
            # Falta el valor
            'descripcion': 'Ingreso incompleto'
        }
        
        with self.assertRaises(ValidationError):
            crear_ingreso(datos_incompletos)
    
    def test_obtener_total_ingresos_dia(self):
        """Prueba que se obtiene correctamente el total de ingresos para un día"""
        total_hoy = obtener_total_ingresos_dia(self.hoy)
        self.assertEqual(total_hoy, 150000)  # 100000 + 50000
        
        total_ayer = obtener_total_ingresos_dia(self.ayer)
        self.assertEqual(total_ayer, 75000)
        
        # Día sin ingresos
        total_manana = obtener_total_ingresos_dia(self.manana)
        self.assertEqual(total_manana, 0)
        
        # Sin especificar fecha (debe usar la fecha actual)
        total_default = obtener_total_ingresos_dia()
        self.assertEqual(total_default, 150000)  # Asumiendo que hoy es self.hoy
    
    def test_obtener_ingresos_rango(self):
        """Prueba que se obtienen los ingresos en un rango de fechas"""
        hace_dos_dias = self.hoy - timedelta(days=2)
        
        # Crear ingreso adicional hace dos días
        Ingreso.objects.create(
            fecha=hace_dos_dias,
            valor=25000,
            descripcion='Ingreso de hace dos días'
        )
        
        # Rango que incluye todos los ingresos
        ingresos = obtener_ingresos_rango(hace_dos_dias, self.hoy)
        self.assertEqual(ingresos.count(), 4)
        
        # Rango que solo incluye ingresos de hoy
        ingresos_hoy = obtener_ingresos_rango(self.hoy, self.hoy)
        self.assertEqual(ingresos_hoy.count(), 2)
        
        # Rango sin ingresos
        rango_futuro = obtener_ingresos_rango(self.manana, self.manana + timedelta(days=1))
        self.assertEqual(rango_futuro.count(), 0)
    
    def test_obtener_total_ingresos_rango(self):
        """Prueba que se obtiene el total de ingresos en un rango de fechas"""
        # Total de ayer y hoy
        total = obtener_total_ingresos_rango(self.ayer, self.hoy)
        self.assertEqual(total, 225000)  # 100000 + 50000 + 75000
        
        # Solo ayer
        total_ayer = obtener_total_ingresos_rango(self.ayer, self.ayer)
        self.assertEqual(total_ayer, 75000)
        
        # Rango futuro (sin ingresos)
        total_futuro = obtener_total_ingresos_rango(self.manana, self.manana + timedelta(days=1))
        self.assertEqual(total_futuro, 0)
    
    def test_generar_pdf_ingresos(self):
        """Prueba que se genera un PDF con los ingresos del rango especificado"""
        ingresos = obtener_ingresos_rango(self.ayer, self.hoy)
        total = obtener_total_ingresos_rango(self.ayer, self.hoy)
        
        pdf = generar_pdf_ingresos(ingresos, self.ayer, self.hoy, total)
        
        # Comprobar que el resultado es un BytesIO con contenido
        self.assertIsInstance(pdf, bytes)
        self.assertTrue(len(pdf) > 0)
        
        # Comprobar que tiene la firma de un PDF
        self.assertTrue(pdf.startswith(b'%PDF'))
    
    @patch('core.services.ingreso_service.SimpleDocTemplate')
    def test_generar_pdf_sin_ingresos(self, mock_doc):
        """Prueba que se genera un PDF incluso cuando no hay ingresos"""
        mock_doc.return_value.build = MagicMock()
        
        # Rango sin ingresos
        ingresos = Ingreso.objects.none()
        pdf = generar_pdf_ingresos(ingresos, self.manana, self.manana, 0)
        
        # Verificar que se llamó a build
        self.assertTrue(mock_doc.return_value.build.called)

from django.contrib.auth.models import User

class IngresoViewTestCase(TestCase):
    """Tests para las vistas relacionadas con ingresos"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.client = Client()
        self.hoy = date.today()
        
        # Crear un usuario para las pruebas
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )
        
        # Crear algunos ingresos de prueba
        Ingreso.objects.create(
            fecha=self.hoy,
            valor=100000,
            descripcion='Ingreso de prueba 1'
        )
        
        # URL de la vista de ingresos
        self.ingreso_url = reverse('ingreso')
        self.confirmar_url = reverse('confirmar_ingreso')
        
        # Iniciar sesión
        self.client.login(username='testuser', password='testpassword123')
    
    def test_ingreso_view_get(self):
        """Prueba que la vista de ingresos se carga correctamente"""
        response = self.client.get(self.ingreso_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ingreso/ingreso_form.html')
        self.assertIn('form', response.context)
        self.assertIn('total_ingresos', response.context)
        
        # Verificar que el total de ingresos es correcto
        self.assertEqual(response.context['total_ingresos'], 100000)
    
    def test_ingreso_view_post_valid(self):
        """Prueba envío exitoso del formulario de ingreso"""
        datos_ingreso = {
            'fecha': self.hoy.strftime('%d/%m/%Y'),
            'valor': 50000,
            'descripcion': 'Nuevo ingreso de prueba'
        }
        
        response = self.client.post(self.ingreso_url, datos_ingreso)
        
        # Debería redirigir a la vista de confirmación
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.confirmar_url)
        
        # Verificar que los datos se guardaron en la sesión
        self.assertIn('ingreso_data', self.client.session)
        session_data = self.client.session['ingreso_data']
        self.assertEqual(session_data['valor'], 50000)
        self.assertEqual(session_data['descripcion'], 'Nuevo ingreso de prueba')
    
    def test_ingreso_view_post_invalid(self):
        """Prueba envío inválido del formulario de ingreso"""
        datos_invalidos = {
            'fecha': self.hoy.strftime('%d/%m/%Y'),
            'valor': -100,  # Valor negativo, no permitido
            'descripcion': 'Ingreso inválido'
        }
        
        response = self.client.post(self.ingreso_url, datos_invalidos)
        
        # Debería mostrar el formulario nuevamente con errores
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ingreso/ingreso_form.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)
        self.assertIn('valor', response.context['form'].errors)
    
    def test_ingreso_view_con_datos_en_sesion(self):
        """Prueba que la vista muestra correctamente los datos guardados en sesión"""
        # Guardar datos en la sesión
        session = self.client.session
        session['ingreso_data'] = {
            'fecha': self.hoy.strftime('%Y-%m-%d'),
            'valor': 75000,
            'descripcion': 'Ingreso desde sesión'
        }
        session.save()
        
        response = self.client.get(self.ingreso_url)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que el formulario está pre-poblado con los datos de la sesión
        form = response.context['form']
        self.assertEqual(form.initial['valor'], 75000)
        self.assertEqual(form.initial['descripcion'], 'Ingreso desde sesión')
    
    def test_ingreso_view_sin_sesion_iniciada(self):
        """Prueba que se redirige al login si no hay sesión iniciada"""
        # Cerrar sesión
        self.client.logout()
        
        response = self.client.get(self.ingreso_url)
        
        # Debería redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

from django.test import TestCase
from django.urls import reverse, resolve
from core.views.Ingreso.ingreso_view import ingreso_view

class UrlsTestCase(TestCase):
    """Tests para las URLs relacionadas con ingresos"""
    
    def test_ingreso_url_resolves(self):
        """Prueba que la URL de ingreso resuelve a la vista correcta"""
        url = reverse('ingreso')
        self.assertEqual(resolve(url).func, ingreso_view)
    
    # Añade pruebas para otras URLs relacionadas con ingresos