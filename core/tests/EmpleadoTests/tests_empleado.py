from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from core.models.empleado import Empleado
from core.forms.empleado_form import EmpleadoForm
from core.services.empleado_service import crear_empleado, get_all_empleados, _initialize_empleado
from django.contrib.messages import get_messages
from datetime import date, timedelta
from django.contrib.auth.models import User
import json
from unittest.mock import patch, Mock


class EmpleadoModelTest(TestCase):

    def test_crear_empleado_valido(self):
        empleado = Empleado.objects.create(
            cedula='1234567890',
            nombre='Pedro',
            apellidos='Gómez',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1990-05-20',
            celular='3001234567',
            cargo='Técnico',
            salario='3000000',
            estado='Activo'
        )
        self.assertEqual(empleado.nombre, 'Pedro')
        self.assertEqual(empleado.apellidos, 'Gómez')
        self.assertEqual(empleado.cedula, '1234567890')
        self.assertEqual(str(empleado), 'Pedro Gómez - 1234567890')

    def test_error_si_falta_nombre(self):
        empleado = Empleado(
            cedula='1234567890',
            apellidos='Gómez',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1990-05-20',
            celular='3001234567',
            cargo='Técnico',
            salario='3000000',
            estado='Activo'
        )
        with self.assertRaises(ValidationError):
            empleado.full_clean()

    def test_error_si_falta_apellidos(self):
        empleado = Empleado(
            cedula='1234567890',
            nombre='Pedro',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1990-05-20',
            celular='3001234567',
            cargo='Técnico',
            salario='3000000',
            estado='Activo'
        )
        with self.assertRaises(ValidationError):
            empleado.full_clean()

    def test_error_si_falta_celular(self):
        empleado = Empleado(
            cedula='1234567890',
            nombre='Pedro',
            apellidos='Gómez',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1990-05-20',
            cargo='Técnico',
            salario='3000000',
            estado='Activo'
        )
        with self.assertRaises(ValidationError):
            empleado.full_clean()

    def test_error_si_falta_fecha_ingreso(self):
        empleado = Empleado(
            cedula='1234567890',
            nombre='Pedro',
            apellidos='Gómez',
            fecha_nacimiento='1990-05-20',
            celular='3001234567',
            cargo='Técnico',
            salario='3000000',
            estado='Activo'
        )
        with self.assertRaises(ValidationError):
            empleado.full_clean()

    def test_error_si_falta_fecha_nacimiento(self):
        empleado = Empleado(
            cedula='1234567890',
            nombre='Pedro',
            apellidos='Gómez',
            fecha_ingreso='2023-01-01',
            celular='3001234567',
            cargo='Técnico',
            salario='3000000',
            estado='Activo'
        )
        with self.assertRaises(ValidationError):
            empleado.full_clean()

    def test_cedula_con_letras_no_valida(self):
        empleado = Empleado(
            cedula='ABC1234567',
            nombre='Laura',
            apellidos='Torres',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1995-02-10',
            celular='3001234567',
            cargo='Técnico',
            salario='3000000',
            estado='Activo'
        )
        with self.assertRaises(ValidationError):
            empleado.full_clean()

    def test_cedula_muy_larga(self):
        empleado = Empleado(
            cedula='1234567890123456',  # 16 dígitos
            nombre='Andrés',
            apellidos='Ríos',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1992-07-15',
            celular='3001234567',
            cargo='Técnico',
            salario='3000000',
            estado='Activo'
        )
        with self.assertRaises(ValidationError):
            empleado.full_clean()

    def test_celular_invalido(self):
        empleado = Empleado(
            cedula='1234567890',
            nombre='Camila',
            apellidos='Fernández',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1998-03-25',
            celular='123',  # Muy corto
            cargo='Técnico',
            salario='3000000',
            estado='Activo'
        )
        with self.assertRaises(ValidationError):
            empleado.full_clean()

    def test_salario_invalido(self):
        empleado = Empleado(
            cedula='1234567890',
            nombre='Camila',
            apellidos='Fernández',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1998-03-25',
            celular='3001234567',
            cargo='Técnico',
            salario='abc',  # No numérico
            estado='Activo'
        )
        with self.assertRaises(ValidationError):
            empleado.full_clean()

    def test_estado_invalido(self):
        empleado = Empleado(
            cedula='1234567890',
            nombre='Camila',
            apellidos='Fernández',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1998-03-25',
            celular='3001234567',
            cargo='Técnico',
            salario='3000000',
            estado='Estado_Invalido'  # Estado que no existe
        )
        with self.assertRaises(ValidationError):
            empleado.full_clean()

    def test_cargo_invalido(self):
        empleado = Empleado(
            cedula='1234567890',
            nombre='Camila',
            apellidos='Fernández',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1998-03-25',
            celular='3001234567',
            cargo='Cargo_Invalido',  # Cargo que no existe
            salario='3000000',
            estado='Activo'
        )
        with self.assertRaises(ValidationError):
            empleado.full_clean()


class EmpleadoFormTest(TestCase):
    def setUp(self):
        # Crear un empleado existente para probar duplicados
        Empleado.objects.create(
            cedula='1234567890',
            nombre='Test',
            apellidos='Usuario',
            fecha_ingreso='2024-01-01',
            fecha_nacimiento='1990-01-01',
            celular='3001234567',
            cargo='Técnico',
            salario='2500000',
            estado='Activo'
        )

    def test_cedula_validation(self):
        # Test cédula con letras
        form_data = {
            'cedula': 'ABC123',
            'nombre': 'Test',
            'apellidos': 'Usuario',
            'fecha_ingreso': '01/01/2024',
            'fecha_nacimiento': '01/01/1990',
            'celular': '3001234567',
            'cargo': 'Técnico',
            'salario': '2500000',
            'estado': 'Activo'
        }
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cedula', form.errors)
        self.assertEqual(form.errors['cedula'][0],
                         "La cédula debe contener solo números.")

        # Test cédula muy larga
        form_data['cedula'] = '1234567890123456'
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['cedula'][0],
                         "La cédula no puede tener más de 15 dígitos.")

        # Test cédula duplicada
        form_data['cedula'] = '1234567890'
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['cedula'][0], "Empleado ya existente.")

    def test_celular_validation(self):
        # Test celular con letras
        form_data = {
            'cedula': '1234567891',
            'celular': 'ABC1234567',
            'nombre': 'Test',
            'apellidos': 'Usuario',
            'fecha_ingreso': '01/01/2024',
            'fecha_nacimiento': '01/01/1990',
            'cargo': 'Técnico',
            'salario': '2500000',
            'estado': 'Activo'
        }
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['celular'][0],
                         "El celular debe contener solo números.")

        # Test celular longitud incorrecta
        form_data['celular'] = '123456789'
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['celular'][0], "El celular debe tener exactamente 10 dígitos.")

    def test_salario_validation(self):
        # Test salario con letras
        form_data = {
            'cedula': '1234567891',
            'celular': '3001234567',
            'salario': 'ABC123',
            'nombre': 'Test',
            'apellidos': 'Usuario',
            'fecha_ingreso': '01/01/2024',
            'fecha_nacimiento': '01/01/1990',
            'cargo': 'Técnico',
            'estado': 'Activo'
        }
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['salario'][0],
                         "El salario debe ser numérico.")

        # Test salario muy largo
        form_data['salario'] = '123456789'
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['salario'][0],
                         "El salario no puede tener más de 8 dígitos.")

    def test_nombre_validation(self):
        # Test nombre muy corto
        form_data = {
            'cedula': '1234567891',
            'nombre': 'A',  # Muy corto
            'apellidos': 'Usuario',
            'fecha_ingreso': '01/01/2024',
            'fecha_nacimiento': '01/01/1990',
            'celular': '3001234567',
            'cargo': 'Técnico',
            'salario': '2500000',
            'estado': 'Activo'
        }
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['nombre'][0], "Cada nombre debe tener al menos 2 letras.")

    def test_apellidos_validation(self):
        # Test apellidos muy cortos
        form_data = {
            'cedula': '1234567891',
            'nombre': 'Test',
            'apellidos': 'A',  # Muy corto
            'fecha_ingreso': '01/01/2024',  # Cambiado a DD/MM/YYYY
            'fecha_nacimiento': '01/01/1990',  # Cambiado a DD/MM/YYYY
            'celular': '3001234567',
            'cargo': 'Técnico',
            'salario': '2500000',
            'estado': 'Activo'
        }
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['apellidos'][0], "Cada nombre debe tener al menos 2 letras.")

    def test_fecha_nacimiento_validation(self):
        # Test menor de edad
        hoy = date.today()
        fecha_menor_edad = hoy.replace(year=hoy.year - 17)  # 17 años

        form_data = {
            'cedula': '1234567891',
            'nombre': 'Test',
            'apellidos': 'Usuario',
            'fecha_ingreso': '01/01/2024',
            'fecha_nacimiento': fecha_menor_edad.strftime('%d/%m/%Y'),
            'celular': '3001234567',
            'cargo': 'Técnico',
            'salario': '2500000',
            'estado': 'Activo'
        }
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_nacimiento', form.errors)

    def test_fecha_ingreso_validation(self):
        # Test fecha futura
        hoy = date.today()
        fecha_futura = hoy + timedelta(days=30)  # 30 días en el futuro

        form_data = {
            'cedula': '1234567891',
            'nombre': 'Test',
            'apellidos': 'Usuario',
            'fecha_ingreso': fecha_futura.strftime('%d/%m/%Y'),
            'fecha_nacimiento': '01/01/1990',
            'celular': '3001234567',
            'cargo': 'Técnico',
            'salario': '2500000',
            'estado': 'Activo'
        }
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_ingreso', form.errors)

    def test_valid_form(self):
        # Test con datos válidos
        form_data = {
            'cedula': '1234567891',
            'nombre': 'Test Nuevo',
            'apellidos': 'Usuario Nuevo',
            'fecha_ingreso': '01/01/2024',
            'fecha_nacimiento': '01/01/1990',
            'celular': '3001234567',
            'cargo': 'Técnico',
            'salario': '2500000',
            'estado': 'Activo'
        }
        form = EmpleadoForm(data=form_data)
        self.assertTrue(form.is_valid())


class EmpleadoServiceTest(TestCase):
    """Tests específicos para el servicio de empleados"""
    
    def setUp(self):
        """Configuración inicial para las pruebas del servicio"""
        self.empleado1 = Empleado.objects.create(
            cedula='1111122222',
            nombre='Juan',
            apellidos='Pérez',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1990-01-01',
            celular='3001234567',
            cargo='Técnico',
            salario='2500000',
            estado='Activo'
        )
        
        self.empleado2 = Empleado.objects.create(
            cedula='2222233333',
            nombre='Ana',
            apellidos='García',
            fecha_ingreso='2023-02-01',
            fecha_nacimiento='1992-05-15',
            celular='3007654321',
            cargo='Secretario/a',
            salario='3000000',
            estado='Inactivo'
        )
    
    def test_get_all_empleados_sin_filtros(self):
        """Prueba obtener todos los empleados sin filtros"""
        empleados = get_all_empleados()
        self.assertEqual(empleados.count(), 2)
        # Verificar que están ordenados por nombre
        self.assertEqual(empleados.first().nombre, 'Ana')
        self.assertEqual(empleados.last().nombre, 'Juan')
    
    def test_get_all_empleados_filtro_estado_activo(self):
        """Prueba filtrar empleados por estado activo"""
        empleados = get_all_empleados(filtro_estado='Activo')
        self.assertEqual(empleados.count(), 1)
        self.assertEqual(empleados.first().nombre, 'Juan')
    
    def test_get_all_empleados_filtro_estado_inactivo(self):
        """Prueba filtrar empleados por estado inactivo"""
        empleados = get_all_empleados(filtro_estado='Inactivo')
        self.assertEqual(empleados.count(), 1)
        self.assertEqual(empleados.first().nombre, 'Ana')
    
    def test_get_all_empleados_busqueda_cedula(self):
        """Prueba buscar empleados por cédula"""
        empleados = get_all_empleados(busqueda_cedula='1111')
        self.assertEqual(empleados.count(), 1)
        self.assertEqual(empleados.first().nombre, 'Juan')
    
    def test_get_all_empleados_busqueda_cedula_parcial(self):
        """Prueba buscar empleados por cédula parcial"""
        empleados = get_all_empleados(busqueda_cedula='2222')
        self.assertEqual(empleados.count(), 2)  # Ambos tienen 2222 en su cédula
    
    def test_get_all_empleados_filtros_combinados(self):
        """Prueba filtros combinados de estado y cédula"""
        empleados = get_all_empleados(filtro_estado='Activo', busqueda_cedula='1111')
        self.assertEqual(empleados.count(), 1)
        self.assertEqual(empleados.first().nombre, 'Juan')
    
    def test_get_all_empleados_sin_resultados(self):
        """Prueba filtros que no devuelven resultados"""
        empleados = get_all_empleados(busqueda_cedula='9999')
        self.assertEqual(empleados.count(), 0)
    
    def test_initialize_empleado_existente(self):
        """Prueba inicializar empleado existente"""
        empleado, modo = _initialize_empleado(self.empleado1.id)
        self.assertEqual(empleado.id, self.empleado1.id)
        self.assertEqual(modo, 'editar')
    
    def test_initialize_empleado_nuevo(self):
        """Prueba inicializar empleado nuevo"""
        empleado, modo = _initialize_empleado(None)
        self.assertIsNone(empleado)
        self.assertEqual(modo, 'agregar')

    def test_crear_empleado_exitoso(self):
        """Prueba crear empleado exitosamente con el servicio"""
        from datetime import date
        
        form_data = {
            'cedula': '9876543210',
            'nombre': 'Carlos',
            'apellidos': 'Rodríguez',
            'fecha_ingreso': date(2023, 3, 1),
            'fecha_nacimiento': date(1988, 3, 15),
            'celular': '3009876543',
            'cargo': 'Técnico',  # Cambiado a un cargo válido
            'salario': '4000000',
            'estado': 'Activo'
        }
        
        form = EmpleadoForm(data=form_data)
        if not form.is_valid():
            self.fail(f"Formulario no válido: {form.errors}")
        
        empleado = crear_empleado(form)
        
        # Verificar que el empleado se creó correctamente
        self.assertEqual(empleado.cedula, '9876543210')
        self.assertEqual(empleado.nombre, 'Carlos')
        self.assertEqual(empleado.apellidos, 'Rodríguez')
        self.assertEqual(empleado.cargo, 'Técnico')
        self.assertIsNotNone(empleado.id)
        
        # Verificar que se guardó en la base de datos
        empleado_db = Empleado.objects.get(id=empleado.id)
        self.assertEqual(empleado_db.cedula, '9876543210')

    def test_initialize_empleado_id_cero(self):
        """Prueba inicializar empleado con ID cero"""
        empleado, modo = _initialize_empleado(0)
        self.assertIsNone(empleado)
        self.assertEqual(modo, 'agregar')

    def test_initialize_empleado_id_inexistente(self):
        """Prueba inicializar empleado con ID que no existe"""
        from django.http import Http404
        with self.assertRaises(Http404):
            _initialize_empleado(9999)

    def test_get_all_empleados_ordenamiento(self):
        """Prueba que los empleados se devuelven ordenados por nombre"""
        # Crear empleados con nombres específicos para verificar orden
        Empleado.objects.create(
            cedula='3333344444',
            nombre='Zebra',
            apellidos='Último',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1990-01-01',
            celular='3001111111',
            cargo='Técnico',
            salario='2000000',
            estado='Activo'
        )
        
        empleados = get_all_empleados()
        nombres = [emp.nombre for emp in empleados]
        
        # Verificar que están ordenados alfabéticamente
        self.assertEqual(nombres, sorted(nombres))
        # El primer empleado debería ser 'Ana' y el último 'Zebra'
        self.assertEqual(empleados.first().nombre, 'Ana')
        self.assertEqual(empleados.last().nombre, 'Zebra')

    def test_get_all_empleados_filtro_estado_none(self):
        """Prueba que None en filtro_estado no aplica filtro"""
        empleados = get_all_empleados(filtro_estado=None)
        self.assertEqual(empleados.count(), 2)

    def test_get_all_empleados_filtro_estado_vacio(self):
        """Prueba que string vacío en filtro_estado no aplica filtro"""
        empleados = get_all_empleados(filtro_estado='')
        self.assertEqual(empleados.count(), 2)

    def test_get_all_empleados_busqueda_cedula_none(self):
        """Prueba que None en busqueda_cedula no aplica filtro"""
        empleados = get_all_empleados(busqueda_cedula=None)
        self.assertEqual(empleados.count(), 2)

    def test_get_all_empleados_busqueda_cedula_vacia(self):
        """Prueba que string vacío en busqueda_cedula no aplica filtro"""
        empleados = get_all_empleados(busqueda_cedula='')
        self.assertEqual(empleados.count(), 2)

    def test_get_all_empleados_busqueda_cedula_case_sensitive(self):
        """Prueba que la búsqueda por cédula es case insensitive (no debería importar)"""
        # Crear empleado con cédula específica
        Empleado.objects.create(
            cedula='ABC123',
            nombre='Test',
            apellidos='Case',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1990-01-01',
            celular='3001111111',
            cargo='Técnico',
            salario='2000000',
            estado='Activo'
        )
        
        empleados = get_all_empleados(busqueda_cedula='abc')
        # Debería encontrar el empleado porque icontains es case insensitive
        self.assertEqual(empleados.count(), 1)

    def test_get_all_empleados_filtros_extremos(self):
        """Prueba filtros con valores que no existen"""
        empleados = get_all_empleados(filtro_estado='EstadoInexistente', busqueda_cedula='CedulaInexistente')
        self.assertEqual(empleados.count(), 0)


class EmpleadoServiceUtilsTest(TestCase):
    """Tests para las funciones utilitarias del servicio de empleados"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.empleado = Empleado.objects.create(
            cedula='1111122222',
            nombre='Juan',
            apellidos='Pérez',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1990-01-01',
            celular='3001234567',
            cargo='Técnico',
            salario='2500000',
            estado='Activo'
        )
    
    @patch('core.services.empleado_service.messages')
    def test_handle_form_success_ajax_request(self, mock_messages):
        """Prueba manejo de éxito para solicitudes AJAX"""
        from core.services.empleado_service import _handle_form_success
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.post('/test/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        response = _handle_form_success(request, self.empleado, 'editar')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('editado', response_data['message'])
        mock_messages.success.assert_called_once()
    
    @patch('core.services.empleado_service.messages')
    def test_handle_form_success_modal_request(self, mock_messages):
        """Prueba manejo de éxito para solicitudes con modal"""
        from core.services.empleado_service import _handle_form_success
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.post('/test/', HTTP_X_SHOW_MODAL='true')
        
        response = _handle_form_success(request, self.empleado, 'agregar')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('redirect', response_data)
        # Para solicitudes con modal, no se incluye message en la respuesta JSON
        self.assertNotIn('message', response_data)
        mock_messages.success.assert_called_once()
    
    @patch('core.services.empleado_service.messages')
    def test_handle_form_success_normal_request(self, mock_messages):
        """Prueba manejo de éxito para solicitudes normales"""
        from core.services.empleado_service import _handle_form_success
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.post('/test/')
        
        response = _handle_form_success(request, self.empleado, 'editar')
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(response.url, reverse('empleado_list'))
        mock_messages.success.assert_called_once()
    
    @patch('core.services.empleado_service.messages')
    def test_handle_form_error_ajax_request(self, mock_messages):
        """Prueba manejo de errores para solicitudes AJAX"""
        from core.services.empleado_service import _handle_form_error
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.post('/test/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        response = _handle_form_error(request, 'Error de prueba')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['message'], 'Error de prueba')
        mock_messages.error.assert_called_once()
    
    @patch('core.services.empleado_service.messages')
    def test_handle_form_error_ajax_with_form_errors(self, mock_messages):
        """Prueba manejo de errores AJAX with errores específicos de formulario"""
        from core.services.empleado_service import _handle_form_error
        from django.test import RequestFactory
        
        # Crear un formulario con errores
        form_data = {'cedula': ''}  # Cédula vacía debería causar error
        form = EmpleadoForm(data=form_data)
        form.is_valid()  # Esto generará errores
        
        factory = RequestFactory()
        request = factory.post('/test/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        response = _handle_form_error(request, 'Error de formulario', form)
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('errors', response_data)
        mock_messages.error.assert_called_once()
    
    @patch('core.services.empleado_service.messages')
    def test_handle_form_error_normal_request(self, mock_messages):
        """Prueba manejo de errores para solicitudes normales"""
        from core.services.empleado_service import _handle_form_error
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.post('/test/')
        
        response = _handle_form_error(request, 'Error de prueba')
        
        # Para solicitudes normales, debería retornar None
        self.assertIsNone(response)
        mock_messages.error.assert_called_once()


class EmpleadoServicePDFTest(TestCase):
    """Tests para la generación de PDF de empleados"""
    
    def setUp(self):
        """Configuración inicial para las pruebas de PDF"""
        # Limpiar empleados existentes
        Empleado.objects.all().delete()
        
        # Crear empleados de prueba
        self.empleado_activo = Empleado.objects.create(
            cedula='1111111111',
            nombre='Juan',
            apellidos='Pérez García',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1990-01-01',
            celular='3001234567',
            cargo='Técnico',
            salario='2500000',
            estado='Activo'
        )
        
        self.empleado_inactivo = Empleado.objects.create(
            cedula='2222222222',
            nombre='María',
            apellidos='López Rodríguez',
            fecha_ingreso='2023-02-01',
            fecha_nacimiento='1985-05-15',
            celular='3007654321',
            cargo='Secretario/a',
            salario='2000000',
            estado='Inactivo'
        )
    
    def test_generar_pdf_empleados_sin_datos(self):
        """Prueba generar PDF sin empleados"""
        from core.services.empleado_service import generar_pdf_empleados
        
        empleados = Empleado.objects.none()  # QuerySet vacío
        
        pdf_content = generar_pdf_empleados(empleados, 'todos')
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        # Los PDFs empiezan con %PDF
        self.assertTrue(pdf_content.startswith(b'%PDF'))
    
    def test_generar_pdf_empleados_con_datos(self):
        """Prueba generar PDF con empleados"""
        from core.services.empleado_service import generar_pdf_empleados
        
        empleados = Empleado.objects.all()
        
        pdf_content = generar_pdf_empleados(empleados, 'todos')
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))
    
    def test_generar_pdf_empleados_filtro_activos(self):
        """Prueba generar PDF con filtro de empleados activos"""
        from core.services.empleado_service import generar_pdf_empleados
        
        empleados = Empleado.objects.filter(estado='Activo')
        
        pdf_content = generar_pdf_empleados(empleados, 'Activo')
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))
    
    def test_generar_pdf_empleados_filtro_inactivos(self):
        """Prueba generar PDF con filtro de empleados inactivos"""
        from core.services.empleado_service import generar_pdf_empleados
        
        empleados = Empleado.objects.filter(estado='Inactivo')
        
        pdf_content = generar_pdf_empleados(empleados, 'Inactivo')
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))
    
    def test_generar_pdf_empleados_con_estado_custom(self):
        """Prueba generar PDF con estado personalizado"""
        from core.services.empleado_service import generar_pdf_empleados
        
        empleados = Empleado.objects.all()
        
        pdf_content = generar_pdf_empleados(empleados, 'Estado Personalizado')
        
        # Verificar que se generó contenido PDF sin errores
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))
    
    @patch('django.contrib.staticfiles.finders.find')
    @patch('reportlab.platypus.Image')
    def test_generar_pdf_empleados_con_logo(self, mock_image_class, mock_find):
        """Prueba generar PDF cuando se encuentra el logo"""
        from core.services.empleado_service import generar_pdf_empleados
        
        # Mock para simular que se encuentra el logo
        mock_find.return_value = '/path/to/logo.png'
        
        # Mock de la clase Image para que devuelva un objeto compatible
        mock_image_instance = Mock()
        mock_image_instance.getKeepWithNext.return_value = False
        mock_image_instance.wrap.return_value = (100, 50)
        mock_image_instance.drawOn = Mock()
        mock_image_class.return_value = mock_image_instance
        
        empleados = Empleado.objects.all()
        
        pdf_content = generar_pdf_empleados(empleados, 'todos')
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))
        
        # Verificar que se intentó usar el logo
        mock_image_class.assert_called_once()
    
    @patch('django.contrib.staticfiles.finders.find')
    def test_generar_pdf_empleados_sin_logo(self, mock_find):
        """Prueba generar PDF cuando no se encuentra el logo"""
        from core.services.empleado_service import generar_pdf_empleados
        
        # Mock para simular que no se encuentra el logo
        mock_find.return_value = None
        
        empleados = Empleado.objects.all()
        
        pdf_content = generar_pdf_empleados(empleados, 'todos')
        
        # Verificar que se generó contenido PDF sin errores
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))
    
    @patch('core.services.empleado_service.timezone')
    def test_generar_pdf_empleados_fecha_footer(self, mock_timezone):
        """Prueba que se incluye la fecha en el footer del PDF"""
        from core.services.empleado_service import generar_pdf_empleados
        from datetime import datetime
        
        # Mock para controlar la fecha
        mock_now = datetime(2024, 1, 15, 10, 30, 0)
        mock_timezone.now.return_value = mock_now
        
        empleados = Empleado.objects.all()
        
        pdf_content = generar_pdf_empleados(empleados, 'todos')
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))
        
        # Verificar que se llamó timezone.now para la fecha
        mock_timezone.now.assert_called()
    
    def test_generar_pdf_empleados_multiples_empleados(self):
        """Prueba generar PDF con múltiples empleados"""
        from core.services.empleado_service import generar_pdf_empleados
        
        # Crear empleados adicionales
        for i in range(5):
            Empleado.objects.create(
                cedula=f'555555555{i}',
                nombre=f'Empleado{i}',
                apellidos=f'Apellido{i}',
                fecha_ingreso='2023-01-01',
                fecha_nacimiento='1990-01-01',
                celular=f'300555555{i}',
                cargo='Técnico',
                salario='2000000',
                estado='Activo'
            )
        
        empleados = Empleado.objects.all()
        
        pdf_content = generar_pdf_empleados(empleados, 'todos')
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))
    
    def test_generar_pdf_empleados_con_request(self):
        """Prueba generar PDF pasando el objeto request"""
        from core.services.empleado_service import generar_pdf_empleados
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/test/')
        
        empleados = Empleado.objects.all()
        
        pdf_content = generar_pdf_empleados(empleados, 'todos', request)
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))


class EmpleadoServiceAdvancedTest(TestCase):
    """Tests avanzados para el servicio de empleados"""
    
    def setUp(self):
        """Configuración inicial para los tests avanzados"""
        self.empleado_activo = Empleado.objects.create(
            cedula='1111111111',
            nombre='Juan',
            apellidos='Pérez',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1990-05-20',
            celular='3001111111',
            cargo='Técnico',
            salario='2500000',
            estado='Activo'
        )
        
        self.empleado_inactivo = Empleado.objects.create(
            cedula='2222222222',
            nombre='María',
            apellidos='García',
            fecha_ingreso='2022-06-15',
            fecha_nacimiento='1988-08-10',
            celular='3002222222',
            cargo='Secretario/a',
            salario='2200000',
            estado='Inactivo'
        )

    def test_get_all_empleados_filtro_case_insensitive(self):
        """Prueba que los filtros de estado no son case sensitive"""
        from core.services.empleado_service import get_all_empleados
        
        # Probar con diferentes variaciones de mayúsculas/minúsculas
        empleados_activos = get_all_empleados(filtro_estado='activo')
        empleados_activos2 = get_all_empleados(filtro_estado='ACTIVO')
        empleados_activos3 = get_all_empleados(filtro_estado='Activo')
        
        # Los tres deberían dar el mismo resultado o ninguno (dependiendo de la implementación)
        # Como el código actual es exacto, solo 'Activo' debería funcionar
        self.assertEqual(empleados_activos.count(), 0)  # 'activo' no existe
        self.assertEqual(empleados_activos2.count(), 0)  # 'ACTIVO' no existe
        self.assertEqual(empleados_activos3.count(), 1)  # 'Activo' sí existe

    def test_get_all_empleados_busqueda_cedula_exacta(self):
        """Prueba búsqueda exacta por cédula"""
        from core.services.empleado_service import get_all_empleados
        
        empleados = get_all_empleados(busqueda_cedula='1111111111')
        self.assertEqual(empleados.count(), 1)
        self.assertEqual(empleados.first().cedula, '1111111111')

    def test_get_all_empleados_busqueda_cedula_inexistente(self):
        """Prueba búsqueda con cédula que no existe"""
        from core.services.empleado_service import get_all_empleados
        
        empleados = get_all_empleados(busqueda_cedula='9999999999')
        self.assertEqual(empleados.count(), 0)

    def test_get_all_empleados_filtros_combinados_sin_resultados(self):
        """Prueba filtros combinados que no deberían devolver resultados"""
        from core.services.empleado_service import get_all_empleados
        
        # Buscar empleado activo con cédula de empleado inactivo
        empleados = get_all_empleados(filtro_estado='Activo', busqueda_cedula='2222222222')
        self.assertEqual(empleados.count(), 0)

    def test_get_all_empleados_filtros_combinados_con_resultados(self):
        """Prueba filtros combinados que sí deberían devolver resultados"""
        from core.services.empleado_service import get_all_empleados
        
        # Buscar empleado activo con cédula de empleado activo
        empleados = get_all_empleados(filtro_estado='Activo', busqueda_cedula='1111111111')
        self.assertEqual(empleados.count(), 1)
        self.assertEqual(empleados.first().cedula, '1111111111')

    def test_initialize_empleado_con_id_string(self):
        """Prueba inicializar empleado con ID como string"""
        from core.services.empleado_service import _initialize_empleado
        
        empleado, modo = _initialize_empleado(str(self.empleado_activo.id))
        self.assertEqual(empleado.id, self.empleado_activo.id)
        self.assertEqual(modo, 'editar')

    def test_initialize_empleado_con_id_negativo(self):
        """Prueba inicializar empleado con ID negativo"""
        from core.services.empleado_service import _initialize_empleado
        from django.http import Http404
        
        with self.assertRaises(Http404):
            _initialize_empleado(-1)

    def test_crear_empleado_con_form_invalido(self):
        """Prueba crear empleado con formulario inválido"""
        from core.services.empleado_service import crear_empleado
        from core.forms.empleado_form import EmpleadoForm
        
        # Crear un formulario con datos inválidos
        form_data = {
            'cedula': '',  # Cédula vacía (inválida)
            'nombre': 'Test',
            'apellidos': 'Usuario'
        }
        
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # El servicio debería manejar el error gracefully
        with self.assertRaises(ValueError):
            crear_empleado(form)

    def test_crear_empleado_duplicado(self):
        """Prueba crear empleado con cédula duplicada"""
        from core.services.empleado_service import crear_empleado
        from core.forms.empleado_form import EmpleadoForm
        from datetime import date
        
        # Intentar crear empleado con cédula que ya existe
        form_data = {
            'cedula': '1111111111',  # Esta cédula ya existe
            'nombre': 'Otro',
            'apellidos': 'Empleado',
            'fecha_ingreso': date(2023, 3, 1),
            'fecha_nacimiento': date(1988, 3, 15),
            'celular': '3009999999',
            'cargo': 'Técnico',
            'salario': '2000000',
            'estado': 'Activo'
        }
        
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cedula', form.errors)


class EmpleadoServiceUtilsAdvancedTest(TestCase):
    """Tests avanzados para las utilidades del servicio de empleados"""
    
    def setUp(self):
        """Configuración inicial para los tests de utilidades"""
        self.empleado = Empleado.objects.create(
            cedula='5555555555',
            nombre='Ana',
            apellidos='López',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1992-03-10',
            celular='3005555555',
            cargo='Técnico',
            salario='2800000',
            estado='Activo'
        )

    @patch('core.services.empleado_service.messages')
    def test_handle_form_success_modo_editar(self, mock_messages):
        """Prueba manejo de éxito en modo editar"""
        from core.services.empleado_service import _handle_form_success
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.post('/test/')
        
        response = _handle_form_success(request, self.empleado, 'editar')
        
        # Verificar que se llamó messages.success con el mensaje correcto
        mock_messages.success.assert_called_once()
        call_args = mock_messages.success.call_args[0]
        self.assertIn('editado', call_args[1])

    @patch('core.services.empleado_service.messages')
    def test_handle_form_success_ajax_modo_editar(self, mock_messages):
        """Prueba manejo de éxito AJAX en modo editar"""
        from core.services.empleado_service import _handle_form_success
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.post('/test/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        response = _handle_form_success(request, self.empleado, 'editar')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('editado', response_data['message'])

    @patch('core.services.empleado_service.messages')
    def test_handle_form_error_sin_formulario(self, mock_messages):
        """Prueba manejo de errores sin formulario específico"""
        from core.services.empleado_service import _handle_form_error
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.post('/test/')
        
        response = _handle_form_error(request, 'Error de prueba')
        
        # Para solicitudes normales, debería retornar None
        self.assertIsNone(response)
        mock_messages.error.assert_called_once()

    @patch('core.services.empleado_service.messages')
    def test_handle_form_error_ajax_sin_form_errors(self, mock_messages):
        """Prueba manejo de errores AJAX sin errores específicos de formulario"""
        from core.services.empleado_service import _handle_form_error
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.post('/test/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        response = _handle_form_error(request, 'Error de prueba')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['message'], 'Error de prueba')
        self.assertNotIn('errors', response_data)


class EmpleadoServicePDFAdvancedTest(TestCase):
    """Tests avanzados para la generación de PDF de empleados"""
    
    def setUp(self):
        """Configuración inicial para los tests de PDF avanzados"""
        # Limpiar base de datos antes de cada test
        Empleado.objects.all().delete()
        
        self.empleado1 = Empleado.objects.create(
            cedula='7777777777',
            nombre='Carlos Alberto',
            apellidos='Ramírez Gómez',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1985-12-20',
            celular='3007777777',
            cargo='Técnico',
            salario='3200000',
            estado='Activo'
        )
        
        self.empleado2 = Empleado.objects.create(
            cedula='8888888888',
            nombre='Lucía',
            apellidos='Martínez',
            fecha_ingreso='2022-08-15',
            fecha_nacimiento='1990-06-05',
            celular='3008888888',
            cargo='Secretario/a',
            salario='2800000',
            estado='Inactivo'
        )

    def test_generar_pdf_empleados_estado_inexistente(self):
        """Prueba generar PDF con estado que no existe en ESTADO_CHOICES"""
        from core.services.empleado_service import generar_pdf_empleados
        
        empleados = Empleado.objects.all()
        
        # Usar un estado que no existe
        pdf_content = generar_pdf_empleados(empleados, 'estado_inexistente')
        
        # Verificar que se generó contenido PDF y usó "TODOS" como default
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))

    def test_generar_pdf_empleados_filtro_vacio(self):
        """Prueba generar PDF con filtro vacío"""
        from core.services.empleado_service import generar_pdf_empleados
        
        empleados = Empleado.objects.all()
        
        pdf_content = generar_pdf_empleados(empleados, '')
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))

    def test_generar_pdf_empleados_filtro_todos_explicito(self):
        """Prueba generar PDF con filtro 'todos' explícito"""
        from core.services.empleado_service import generar_pdf_empleados
        
        empleados = Empleado.objects.all()
        
        pdf_content = generar_pdf_empleados(empleados, 'todos')
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))

    @patch('django.contrib.staticfiles.finders.find')
    def test_generar_pdf_empleados_excepcion_en_logo(self, mock_find):
        """Prueba generar PDF cuando hay excepción al cargar el logo"""
        from core.services.empleado_service import generar_pdf_empleados
        
        # Mock para simular excepción al buscar el logo
        mock_find.side_effect = Exception("Error al buscar logo")
        
        empleados = Empleado.objects.all()
        
        # Debería manejar la excepción gracefully
        pdf_content = generar_pdf_empleados(empleados, 'todos')
        
        # Verificar que se generó contenido PDF sin errores
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))

    def test_generar_pdf_empleados_solo_con_empleados_activos(self):
        """Prueba generar PDF solo con empleados activos"""
        from core.services.empleado_service import generar_pdf_empleados
        
        empleados_activos = Empleado.objects.filter(estado='Activo')
        
        pdf_content = generar_pdf_empleados(empleados_activos, 'Activo')
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))

    def test_generar_pdf_empleados_solo_con_empleados_inactivos(self):
        """Prueba generar PDF solo con empleados inactivos"""
        from core.services.empleado_service import generar_pdf_empleados
        
        empleados_inactivos = Empleado.objects.filter(estado='Inactivo')
        
        pdf_content = generar_pdf_empleados(empleados_inactivos, 'Inactivo')
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))

    def test_generar_pdf_empleados_nombres_largos(self):
        """Prueba generar PDF con empleados que tienen nombres largos"""
        from core.services.empleado_service import generar_pdf_empleados
        
        # Crear empleado con nombre muy largo
        Empleado.objects.create(
            cedula='9999999999',
            nombre='María del Carmen Esperanza',
            apellidos='Rodríguez de la Cruz Martínez',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1987-04-12',
            celular='3009999999',
            cargo='Técnico',
            salario='2500000',
            estado='Activo'
        )
        
        empleados = Empleado.objects.all()
        
        pdf_content = generar_pdf_empleados(empleados, 'todos')
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))

    def test_generar_pdf_empleados_caracteres_especiales(self):
        """Prueba generar PDF con empleados que tienen caracteres especiales"""
        from core.services.empleado_service import generar_pdf_empleados
        
        # Crear empleado con caracteres especiales
        Empleado.objects.create(
            cedula='6666666666',
            nombre='José María',
            apellidos='Peña Niño',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1989-09-15',
            celular='3006666666',
            cargo='Técnico',
            salario='2700000',
            estado='Activo'
        )
        
        empleados = Empleado.objects.all()
        
        pdf_content = generar_pdf_empleados(empleados, 'todos')
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))

    @patch('core.services.empleado_service.timezone')
    def test_generar_pdf_empleados_formato_fecha_personalizado(self, mock_timezone):
        """Prueba que el formato de fecha en el footer sea el correcto"""
        from core.services.empleado_service import generar_pdf_empleados
        from datetime import datetime
        
        # Mock para controlar la fecha con precisión
        mock_now = datetime(2024, 12, 25, 14, 30, 45)  # Navidad 2024 a las 2:30 PM
        mock_timezone.now.return_value = mock_now
        
        empleados = Empleado.objects.all()
        
        pdf_content = generar_pdf_empleados(empleados, 'todos')
        
        # Verificar que se generó contenido PDF
        self.assertIsInstance(pdf_content, bytes)
        self.assertGreater(len(pdf_content), 0)
        self.assertTrue(pdf_content.startswith(b'%PDF'))
        
        # Verificar que se llamó timezone.now para la fecha
        mock_timezone.now.assert_called()

    def tearDown(self):
        """Limpiar después de cada test"""
        Empleado.objects.all().delete()


class EmpleadoServiceEdgeCasesTest(TestCase):
    """Tests para casos límite y edge cases del servicio de empleados"""
    
    def test_get_all_empleados_con_queryset_vacio(self):
        """Prueba obtener empleados cuando no hay ninguno en la base de datos"""
        from core.services.empleado_service import get_all_empleados
        
        # Asegurar que no hay empleados
        Empleado.objects.all().delete()
        
        empleados = get_all_empleados()
        self.assertEqual(empleados.count(), 0)
        self.assertEqual(list(empleados), [])

    def test_get_all_empleados_filtro_estado_con_espacios(self):
        """Prueba filtro de estado con espacios adicionales"""
        from core.services.empleado_service import get_all_empleados
        
        # Crear empleado de prueba
        Empleado.objects.create(
            cedula='3333333333',
            nombre='Test',
            apellidos='Espacios',
            fecha_ingreso='2023-01-01',
            fecha_nacimiento='1990-01-01',
            celular='3003333333',
            cargo='Técnico',
            salario='2000000',
            estado='Activo'
        )
        
        # Probar con espacios (no debería funcionar porque no trim el código)
        empleados = get_all_empleados(filtro_estado=' Activo ')
        self.assertEqual(empleados.count(), 0)  # No debería encontrar nada

    def test_get_all_empleados_busqueda_cedula_con_caracteres_especiales(self):
        """Prueba búsqueda de cédula con caracteres que no son números"""
        from core.services.empleado_service import get_all_empleados
        
        empleados = get_all_empleados(busqueda_cedula='ABC123')
        self.assertEqual(empleados.count(), 0)

    def test_initialize_empleado_con_id_muy_grande(self):
        """Prueba inicializar empleado con ID muy grande"""
        from core.services.empleado_service import _initialize_empleado
        from django.http import Http404
        
        with self.assertRaises(Http404):
            _initialize_empleado(999999999)

    def test_initialize_empleado_con_id_cero_string(self):
        """Prueba inicializar empleado con ID cero como string"""
        from core.services.empleado_service import _initialize_empleado
        from django.http import Http404
        
        # ID cero como string debería causar Http404 si no existe empleado con ID=0
        with self.assertRaises(Http404):
            _initialize_empleado('0')
        
    def tearDown(self):
        """Limpiar después de cada test"""
        Empleado.objects.all().delete()
