from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from core.models.empleado import Empleado
from core.forms.empleado_form import EmpleadoForm
from core.services.empleado_service import crear_empleado, get_all_empleados
from django.contrib.messages import get_messages


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
            'fecha_ingreso': '2024-01-01',
            'fecha_nacimiento': '1990-01-01',
            'celular': '3001234567',
            'cargo': 'Técnico',
            'salario': '2500000',
            'estado': 'Activo'
        }
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cedula', form.errors)
        self.assertEqual(form.errors['cedula'][0], "La cédula debe contener solo números.")

        # Test cédula muy larga
        form_data['cedula'] = '1234567890123456'
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['cedula'][0], "La cédula no puede tener más de 15 dígitos.")

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
            'fecha_ingreso': '2024-01-01',
            'fecha_nacimiento': '1990-01-01',
            'cargo': 'Técnico',
            'salario': '2500000',
            'estado': 'Activo'
        }
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['celular'][0], "El celular debe contener solo números.")

        # Test celular longitud incorrecta
        form_data['celular'] = '123456789'
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['celular'][0], "El celular debe tener exactamente 10 dígitos.")

    def test_salario_validation(self):
        # Test salario con letras
        form_data = {
            'cedula': '1234567891',
            'celular': '3001234567',
            'salario': 'ABC123',
            'nombre': 'Test',
            'apellidos': 'Usuario',
            'fecha_ingreso': '2024-01-01',
            'fecha_nacimiento': '1990-01-01',
            'cargo': 'Técnico',
            'estado': 'Activo'
        }
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['salario'][0], "El salario debe ser numérico.")

        # Test salario muy largo
        form_data['salario'] = '123456789'
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['salario'][0], "El salario no puede tener más de 8 dígitos.")


class EmpleadoServiceTest(TestCase):
    def setUp(self):
        # Crear algunos empleados de prueba
        self.empleado1 = Empleado.objects.create(
            cedula='1234567890',
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
            cedula='0987654321',
            nombre='María',
            apellidos='López',
            fecha_ingreso='2023-02-01',
            fecha_nacimiento='1992-01-01',
            celular='3007654321',
            cargo='Secretario/a',
            salario='2000000',
            estado='Inactivo'
        )

    def test_crear_empleado(self):
        # Preparar datos del formulario
        form_data = {
            'cedula': '1111111111',
            'nombre': 'Pedro',
            'apellidos': 'Gómez',
            'fecha_ingreso': '2024-01-01',
            'fecha_nacimiento': '1995-01-01',
            'celular': '3009876543',
            'cargo': 'Técnico',
            'salario': '3000000',
            'estado': 'Activo'
        }
        form = EmpleadoForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Probar crear_empleado
        empleado = crear_empleado(form)
        self.assertEqual(empleado.nombre, 'Pedro')
        self.assertEqual(empleado.cedula, '1111111111')

    def test_get_all_empleados_sin_filtros(self):
        empleados = get_all_empleados()
        self.assertEqual(empleados.count(), 2)

    def test_get_all_empleados_filtro_estado(self):
        empleados = get_all_empleados(filtro_estado='Activo')
        self.assertEqual(empleados.count(), 1)
        self.assertEqual(empleados[0].nombre, 'Juan')

    def test_get_all_empleados_busqueda_cedula(self):
        empleados = get_all_empleados(busqueda_cedula='123')
        self.assertEqual(empleados.count(), 1)
        self.assertEqual(empleados[0].cedula, '1234567890')

    def test_get_all_empleados_ambos_filtros(self):
        empleados = get_all_empleados(
            filtro_estado='Activo',
            busqueda_cedula='123'
        )
        self.assertEqual(empleados.count(), 1)
        self.assertEqual(empleados[0].nombre, 'Juan')
        
class EmpleadoViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Crear empleados de prueba
        self.empleado1 = Empleado.objects.create(
            cedula='1234567890',
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
            cedula='0987654321',
            nombre='María',
            apellidos='López',
            fecha_ingreso='2023-02-01',
            fecha_nacimiento='1992-01-01',
            celular='3007654321',
            cargo='Secretario/a',
            salario='2000000',
            estado='Inactivo'
        )

    def test_empleado_list_view_sin_filtros(self):
        response = self.client.get(reverse('empleado_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'empleado/empleado_list.html')
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_empleado_list_view_con_filtro_estado(self):
        response = self.client.get(reverse('empleado_list'), {'estado': 'Activo'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['page_obj'][0].estado, 'Activo')

    def test_empleado_list_view_con_busqueda_cedula(self):
        response = self.client.get(reverse('empleado_list'), {'cedula': '123'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['page_obj'][0].cedula, '1234567890')

    def test_empleado_list_view_paginacion(self):
        # Crear más empleados para probar paginación
        for i in range(10):
            Empleado.objects.create(
                cedula=f'11111111{i}',
                nombre=f'Test{i}',
                apellidos='Apellido',
                fecha_ingreso='2023-01-01',
                fecha_nacimiento='1990-01-01',
                celular=f'30012345{i}',
                cargo='Técnico',
                salario='2500000',
                estado='Activo'
            )
        response = self.client.get(reverse('empleado_list'))
        self.assertEqual(len(response.context['page_obj']), 6)  # 6 por página

    def test_empleado_create_view_get(self):
        response = self.client.get(reverse('empleado_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'empleado/empleado_form.html')

    def test_empleado_create_view_post_success(self):
        data = {
            'cedula': '1111111111',
            'nombre': 'Pedro',
            'apellidos': 'Gómez',
            'fecha_ingreso': '2024-01-01',
            'fecha_nacimiento': '1995-01-01',
            'celular': '3009876543',
            'cargo': 'Técnico',
            'salario': '3000000',
            'estado': 'Activo'
        }

        response = self.client.post(reverse('empleado_create'), data)
        self.assertRedirects(response, reverse('empleado_list'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Empleado creado exitosamente.')

    def test_empleado_create_view_post_invalid_form(self):
        data = {
            'cedula': 'invalid',  # Cédula inválida
            'nombre': 'Pedro'
            # Faltan campos requeridos
        }
        response = self.client.post(reverse('empleado_create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'empleado/empleado_form.html')