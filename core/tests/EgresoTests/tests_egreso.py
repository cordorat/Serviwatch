from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from core.models import Egreso
from core.forms import EgresoForm
from datetime import date
from unittest.mock import patch
from core.services.egreso_service import crear_egreso

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
        
    

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from core.models import Egreso
from core.forms import EgresoForm
from datetime import date
from unittest.mock import patch
from django.contrib.messages import get_messages

class EgresoViewTests(TestCase):
    def setUp(self):
        """Configuración inicial para todas las pruebas"""
        self.client = Client()
        self.egreso_url = reverse('egreso')
        self.confirmar_egreso_url = reverse('confirmar_egreso')
        self.session = self.client.session
        self.fecha_hoy = date.today()
        self.datos_prueba = {
            'fecha_str': self.fecha_hoy.isoformat(),
            'valor': 1000,
            'descripcion': 'Test description'
        }

    # Tests para egreso_view GET
    def test_egreso_view_get_sin_sesion(self):
        """Test GET cuando no hay datos en sesión"""
        response = self.client.get(self.egreso_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'egreso/egreso_form.html')
        self.assertIn('form', response.context)
        self.assertIn('total_egresos', response.context)
        self.assertEqual(response.context['total_egresos'], 0)

    def test_egreso_view_get_con_sesion(self):
        """Test GET cuando hay datos en sesión"""
        self.session['datos_egreso'] = self.datos_prueba
        self.session.save()
        response = self.client.get(self.egreso_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'egreso/egreso_form.html')
        self.assertEqual(response.context['form'].initial['valor'], 1000)
        self.assertEqual(response.context['form'].initial['descripcion'], 'Test description')

    def test_egreso_view_get_con_egresos_existentes(self):
        """Test GET verificando suma de egresos existentes"""
        Egreso.objects.create(
            fecha=self.fecha_hoy,
            valor=1000,
            descripcion='Test egreso'
        )
        response = self.client.get(self.egreso_url)
        self.assertEqual(response.context['total_egresos'], 1000)

    # Tests para egreso_view POST
    def test_egreso_view_post_datos_validos(self):
        """Test POST con datos válidos"""
        data = {
            'fecha': self.fecha_hoy,
            'valor': '1000',
            'descripcion': 'Test description'
        }
        response = self.client.post(self.egreso_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.confirmar_egreso_url)
        self.assertIn('datos_egreso', self.client.session)

    def test_egreso_view_post_datos_invalidos_cada_campo(self):
        """Test POST con datos inválidos para cada campo"""
        campos = ['fecha', 'valor', 'descripcion']
        for campo in campos:
            data = {
                'fecha': self.fecha_hoy,
                'valor': '1000',
                'descripcion': 'Test description'
            }
            data[campo] = ''
            response = self.client.post(self.egreso_url, data)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context['form'].errors)
            self.assertIn(campo, response.context['form'].errors)

    # Tests para confirmar_egreso_view
    def test_confirmar_egreso_view_get_sin_sesion(self):
        """Test GET sin datos en sesión"""
        response = self.client.get(self.confirmar_egreso_url)
        self.assertRedirects(response, self.egreso_url)

    def test_confirmar_egreso_view_get_con_sesion(self):
        """Test GET con datos en sesión"""
        # Preparar datos de prueba en la sesión
        self.session['datos_egreso'] = self.datos_prueba
        self.session.save()
        
        # Mock del servicio con la ruta correcta
        with patch('core.views.Egreso.egreso_view.obtener_datos_resumen') as mock_resumen:
            # Configurar el valor de retorno del mock
            mock_resumen.return_value = {
                'total_dia': 1000,
                'total_mes': 5000,
                'promedio_diario': 500
            }
            
            # Realizar la petición GET
            response = self.client.get(self.confirmar_egreso_url)
            
            # Verificaciones
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'egreso/confirmar_egreso.html')
            self.assertIn('resumen', response.context)
            self.assertEqual(response.context['resumen']['total_dia'], 1000)
            self.assertEqual(response.context['resumen']['total_mes'], 5000)
            self.assertEqual(response.context['resumen']['promedio_diario'], 500)
            mock_resumen.assert_called_once()

    def test_confirmar_egreso_view_post_confirmar(self):
        """Test POST confirmando el egreso"""
        # Preparar datos de prueba
        fecha_hoy = date.today()
        self.datos_prueba = {
            'fecha_str': fecha_hoy.isoformat(),
            'valor': 1000,
            'descripcion': 'Test description'
        }
        
        # Guardar en sesión
        self.session['datos_egreso'] = self.datos_prueba
        self.session.save()

        # Mock del servicio usando la ruta correcta desde la vista
        with patch('core.views.Egreso.egreso_view.crear_egreso') as mock_crear:
            # Realizar la petición POST con confirmar
            response = self.client.post(
                self.confirmar_egreso_url, 
                {'confirmar': 'true'},
                follow=True
            )
            
            # Verificar que el mock fue llamado con los argumentos correctos
            expected_data = {
                'fecha': fecha_hoy,
                'valor': 1000,
                'descripcion': 'Test description',
                'fecha_str': fecha_hoy.isoformat()
            }
            mock_crear.assert_called_once_with(expected_data)
            
            # Verificar la respuesta
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'egreso/confirmar_egreso.html')
            self.assertIn('success', response.context)
            self.assertNotIn('datos_egreso', self.client.session)

    def test_confirmar_egreso_view_post_editar(self):
        """Test POST eligiendo editar el egreso"""
        self.session['datos_egreso'] = self.datos_prueba
        self.session.save()
        
        response = self.client.post(self.confirmar_egreso_url, {'editar': True})
        self.assertRedirects(response, self.egreso_url)
        self.assertIn('datos_egreso', self.client.session)

    def test_mensajes_exito(self):
        """Test verificación de mensajes de éxito"""
        self.session['datos_egreso'] = self.datos_prueba
        self.session.save()

        with patch('core.services.egreso_service.crear_egreso'):
            response = self.client.post(self.confirmar_egreso_url, {'confirmar': True})
            messages = list(get_messages(response.wsgi_request))
            self.assertTrue(any(message.message == "Egreso ingresado con éxito" for message in messages))
            self.assertIn('success', response.context)
            self.assertEqual(response.context['success'], 'EGRESO AGREGADO CORRECTAMENTE')