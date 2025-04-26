from django.test import TestCase
from django.core.exceptions import ValidationError
from core.models.empleado import Empleado

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
