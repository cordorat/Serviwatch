from django.test import TestCase
from django.core.exceptions import ValidationError
from core.models.empleado import Empleado
from core.forms.empleado_form import EmpleadoForm


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

