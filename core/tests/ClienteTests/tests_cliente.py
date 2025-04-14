from django.test import TestCase
from django.core.exceptions import ValidationError
from core.models import Cliente

class ClienteModelTest(TestCase):

    def test_crear_cliente_valido(self):
        cliente = Cliente.objects.create(
            nombre='Juan',
            apellido='Pérez',
            telefono='3001234567'
        )
        self.assertEqual(cliente.nombre, 'Juan')
        self.assertEqual(cliente.apellido, 'Pérez')
        self.assertEqual(cliente.telefono, '3001234567')

    def test_error_si_falta_nombre(self):
        cliente = Cliente(
            apellido='Pérez',
            telefono='3001234567'
        )
        with self.assertRaises(ValidationError):
            cliente.full_clean() 

    def test_telefono_con_letras_no_valido(self):
        cliente = Cliente(
            nombre='Ana',
            apellido='López',
            telefono='ABC1234567'
        )
        with self.assertRaises(ValidationError):
            cliente.full_clean()

    def test_telefono_muy_corto(self):
        cliente = Cliente(
            nombre='Carlos',
            apellido='Ramírez',
            telefono='123'
        )
        with self.assertRaises(ValidationError):
            cliente.full_clean()
