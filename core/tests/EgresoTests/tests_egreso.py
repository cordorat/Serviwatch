from django.contrib.messages import get_messages
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from datetime import date
from unittest.mock import patch, MagicMock
from core.models.egreso import Egreso
from core.forms.egreso_form import EgresoForm
from core.services.egreso_service import crear_egreso, crear_egreso_from_data, get_all_egresos
from django.contrib.auth.models import User


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
        """Prueba que la descripción no exceda la longitud máxima"""
        descripcion_larga = 'a' * 111
        self.egreso_data['descripcion'] = descripcion_larga

        with self.assertRaises(Exception):
            egreso = Egreso(**self.egreso_data)
            egreso.full_clean()

    def test_max_digits_valor(self):
        """Prueba que el valor no exceda el número máximo de dígitos"""
        valor_grande = Decimal('12345678901')  # 11 dígitos
        self.egreso_data['valor'] = valor_grande

        with self.assertRaises(Exception):
            egreso = Egreso(**self.egreso_data)
            egreso.full_clean()
            
    def test_str_representation(self):
        """Prueba la representación en cadena del modelo"""
        egreso = Egreso.objects.create(**self.egreso_data)
        expected_str = f"{self.egreso_data['fecha']} - ${self.egreso_data['valor']}"
        self.assertEqual(str(egreso), expected_str)


class EgresoFormTest(TestCase):
    """
    Pruebas unitarias para el formulario EgresoForm
    """

    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.form_data = {
            'valor': '1000',
            'fecha': date.today().strftime('%Y-%m-%d'),
            'descripcion': 'Test descripción'
        }

    def test_form_valid(self):
        """Prueba que el formulario sea válido con datos correctos"""
        form = EgresoForm(data=self.form_data)
        self.assertTrue(form.is_valid(), msg=f"Errores: {form.errors}")

    def test_form_invalid_campo_vacio(self):
        """Prueba que el formulario sea inválido cuando faltan campos"""
        campos_requeridos = ['valor', 'fecha', 'descripcion']

        for campo in campos_requeridos:
            with self.subTest(campo=campo):
                # Crear una copia de los datos
                data_incompleta = self.form_data.copy()
                data_incompleta.pop(campo)

                form = EgresoForm(data=data_incompleta)
                self.assertFalse(form.is_valid())
                self.assertIn(campo, form.errors)
                self.assertIn('', form.errors[campo][0])

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
        self.assertIn('Descripción demasiado larga', form.errors['descripcion'][0])

    def test_valor_demasiado_grande(self):
        """Prueba que se valide el límite máximo de dígitos en el valor"""
        data_invalida = self.form_data.copy()
        data_invalida['valor'] = '12345678901'  # 11 dígitos

        form = EgresoForm(data=data_invalida)
        self.assertFalse(form.is_valid())
        self.assertIn('valor', form.errors)
        self.assertIn('Valor demasiado grande', form.errors['valor'][0])

    def test_valor_negativo(self):
        """Prueba que se valide que el valor no sea negativo"""
        data_invalida = self.form_data.copy()
        data_invalida['valor'] = '-1000'

        form = EgresoForm(data=data_invalida)
        self.assertFalse(form.is_valid())
        self.assertIn('valor', form.errors)


class EgresoServiceTest(TestCase):
    """
    Pruebas unitarias para el servicio de Egreso
    """
    
    def setUp(self):
        self.form_mock = MagicMock()
        self.form_mock.save.return_value = Egreso(
            valor=Decimal('1000.00'),
            fecha=date.today(),
            descripcion='Test descripción'
        )
        
        self.egreso_data = {
            'valor': Decimal('1000.00'),
            'fecha': date.today(),
            'descripcion': 'Test descripción'
        }
        
    def test_crear_egreso(self):
        """Prueba la función crear_egreso"""
        egreso = crear_egreso(self.form_mock)
        self.form_mock.save.assert_called_once()
        self.assertEqual(egreso.valor, Decimal('1000.00'))
        self.assertEqual(egreso.descripcion, 'Test descripción')
        
    def test_crear_egreso_from_data(self):
        """Prueba la función crear_egreso_from_data"""
        egreso = crear_egreso_from_data(
            self.egreso_data['valor'],
            self.egreso_data['fecha'],
            self.egreso_data['descripcion']
        )
        
        self.assertEqual(Egreso.objects.count(), 1)
        egreso_db = Egreso.objects.first()
        self.assertEqual(egreso_db.valor, self.egreso_data['valor'])
        self.assertEqual(egreso_db.descripcion, self.egreso_data['descripcion'])
        
    def test_get_all_egresos(self):
        """Prueba la función get_all_egresos"""
        # Crear egresos de prueba
        Egreso.objects.create(
            valor=Decimal('1000.00'),
            fecha=date(2023, 1, 15),
            descripcion='Egreso enero'
        )
        Egreso.objects.create(
            valor=Decimal('2000.00'),
            fecha=date(2023, 2, 15),
            descripcion='Egreso febrero'
        )
        
        # Probar sin filtros
        egresos = get_all_egresos()
        self.assertEqual(egresos.count(), 2)
        
        # Probar con filtro de fecha inicio
        egresos = get_all_egresos(fecha_inicio=date(2023, 2, 1))
        self.assertEqual(egresos.count(), 1)
        self.assertEqual(egresos.first().descripcion, 'Egreso febrero')
        
        # Probar con filtro de fecha fin
        egresos = get_all_egresos(fecha_fin=date(2023, 1, 31))
        self.assertEqual(egresos.count(), 1)
        self.assertEqual(egresos.first().descripcion, 'Egreso enero')
        
        # Probar con filtro de búsqueda
        egresos = get_all_egresos(busqueda='febrero')
        self.assertEqual(egresos.count(), 1)
        self.assertEqual(egresos.first().descripcion, 'Egreso febrero')


class EgresoViewTests(TestCase):
    def setUp(self):
        """Configuración inicial para todas las pruebas"""
        # Crear usuario para autenticación
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpassword'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
        
        # URLs
        self.egreso_url = reverse('egreso')
        self.confirmar_egreso_url = reverse('confirmar_egreso')
        self.egreso_list_url = reverse('egreso_list')
        
        # Fechas y datos de prueba
        self.fecha_hoy = date.today()
        self.datos_prueba = {
            'valor': '1000',
            'fecha_str': self.fecha_hoy.strftime('%Y-%m-%d'),
            'descripcion': 'Test description'
        }
        
        # Obtener sesión
        self.session = self.client.session

    # Tests para egreso_list_view
    def test_egreso_list_view(self):
        """Test vista de listado de egresos"""
        # Crear algunos egresos para listar
        Egreso.objects.create(
            valor=Decimal('1000.00'),
            fecha=self.fecha_hoy,
            descripcion='Egreso 1'
        )
        Egreso.objects.create(
            valor=Decimal('2000.00'),
            fecha=self.fecha_hoy,
            descripcion='Egreso 2'
        )
        
        response = self.client.get(self.egreso_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'egreso/egreso_list.html')
        self.assertEqual(len(response.context['egresos']), 2)
    
    def test_egreso_list_view_sin_egresos(self):
        """Test vista de listado sin egresos existentes"""
        response = self.client.get(self.egreso_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'egreso/egreso_list.html')
        self.assertEqual(len(response.context['egresos']), 0)
    
    def test_egreso_list_view_con_filtros(self):
        """Test vista de listado con filtros"""
        # Crear egresos en diferentes fechas
        Egreso.objects.create(
            valor=Decimal('1000.00'),
            fecha=date(2023, 1, 15),
            descripcion='Egreso enero'
        )
        Egreso.objects.create(
            valor=Decimal('2000.00'),
            fecha=date(2023, 2, 15),
            descripcion='Egreso febrero'
        )
        
        # Probar filtro por fecha
        response = self.client.get(
            self.egreso_list_url, 
            {'fecha_inicio': '2023-02-01', 'fecha_fin': '2023-02-28'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['egresos']), 1)
        
        # Probar filtro por búsqueda
        response = self.client.get(
            self.egreso_list_url,
            {'busqueda': 'enero'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['egresos']), 1)

    # Tests para egreso_view
    def test_egreso_view_get(self):
        """Test GET de la vista de creación de egreso"""
        response = self.client.get(self.egreso_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'egreso/egreso_form.html')
        self.assertIsInstance(response.context['form'], EgresoForm)

    def test_egreso_view_post_datos_validos(self):
        """Test POST con datos válidos"""
        data = {
            'fecha': self.fecha_hoy.strftime('%Y-%m-%d'),
            'valor': '1000',
            'descripcion': 'Test description'
        }
        response = self.client.post(self.egreso_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.confirmar_egreso_url)
        self.assertIn('datos_egreso', self.client.session)
        
        # Verificar los datos guardados en sesión
        datos_sesion = self.client.session['datos_egreso']
        self.assertEqual(datos_sesion['valor'], '1000')
        self.assertEqual(datos_sesion['descripcion'], 'Test description')

    def test_egreso_view_post_datos_invalidos(self):
        """Test POST con datos inválidos"""
        # Probar con cada campo faltante
        campos = ['fecha', 'valor', 'descripcion']
        for campo in campos:
            with self.subTest(campo=campo):
                data = {
                    'fecha': self.fecha_hoy.strftime('%Y-%m-%d'),
                    'valor': '1000',
                    'descripcion': 'Test description'
                }
                data[campo] = ''
                
                response = self.client.post(self.egreso_url, data)
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, 'egreso/egreso_form.html')
                self.assertIn(campo, response.context['form'].errors)

    def test_egreso_view_post_valor_negativo(self):
        """Test POST con valor negativo"""
        data = {
            'fecha': self.fecha_hoy.strftime('%Y-%m-%d'),
            'valor': '-1000',
            'descripcion': 'Test description'
        }
        response = self.client.post(self.egreso_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('valor', response.context['form'].errors)

    def test_egreso_view_post_fecha_invalida(self):
        """Test POST con fecha inválida"""
        data = {
            'fecha': 'fecha-invalida',
            'valor': '1000',
            'descripcion': 'Test description'
        }
        response = self.client.post(self.egreso_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('fecha', response.context['form'].errors)

    def test_egreso_view_post_descripcion_muy_larga(self):
        """Test POST con descripción demasiado larga"""
        data = {
            'fecha': self.fecha_hoy.strftime('%Y-%m-%d'),
            'valor': '1000',
            'descripcion': 'a' * 101
        }
        response = self.client.post(self.egreso_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('descripcion', response.context['form'].errors)

    # Tests para confirmar_egreso_view
    def test_confirmar_egreso_view_get_sin_datos(self):
        """Test GET sin datos en sesión"""
        # Asegurar que no hay datos en sesión
        if 'datos_egreso' in self.client.session:
            del self.client.session['datos_egreso']
            self.client.session.save()
            
        response = self.client.get(self.confirmar_egreso_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.egreso_url)
        
        # Verificar mensaje de error
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("No hay datos" in str(message) for message in messages))

    def test_confirmar_egreso_view_get_con_datos(self):
        """Test GET con datos en sesión"""
        # Guardar datos en sesión
        session = self.client.session
        session['datos_egreso'] = {
            'valor': '1000',
            'fecha_str': self.fecha_hoy.strftime('%Y-%m-%d'),
            'descripcion': 'Test description'
        }
        session.save()
        
        response = self.client.get(self.confirmar_egreso_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'egreso/confirmar_egreso.html')
        
        # Verificar datos en el contexto
        self.assertIn('datos', response.context)
        datos = response.context['datos']
        self.assertEqual(datos['valor'], '1000')
        self.assertEqual(datos['descripcion'], 'Test description')

    
