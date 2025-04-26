from django.test import TestCase
from core.forms.empleado_form import EmpleadoForm
from core.models.empleado import Empleado
import datetime

class EmpleadoFormTest(TestCase):
    def test_valid_empleado(self):
        form_data = {
            'cedula': '123456789',
            'nombre': 'Juan',
            'apellidos': 'Pérez',
            'fecha_ingreso': datetime.date.today(),
            'fecha_nacimiento': datetime.date(1990, 1, 1),
            'celular': '3001234567',
            'cargo': 'Técnico',
            'salario': '50000',
            'estado': 'Activo'
        }
        form = EmpleadoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_empleado_cedula_repetida(self):
        Empleado.objects.create(
            cedula=123456789, nombre="Juan", apellidos="Pérez",
            fecha_ingreso=datetime.date.today(), fecha_nacimiento=datetime.date(1990, 1, 1),
            celular=3001234567, cargo="Técnico", salario=50000, estado="Activo"
        )

        form_data = {
            'cedula': '123456789',  # misma cédula
            'nombre': 'Pedro',
            'apellidos': 'Gomez',
            'fecha_ingreso': datetime.date.today(),
            'fecha_nacimiento': datetime.date(1995, 5, 5),
            'celular': '3009876543',
            'cargo': 'Secretario/a',
            'salario': '40000',
            'estado': 'Activo'
        }
        form = EmpleadoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cedula', form.errors)
