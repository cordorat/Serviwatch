from django.test import TestCase
from core.models import Reparacion, Cliente, Empleado
from datetime import date


class ReparacionModelTest(TestCase):
    def test_crear_reparacion(self):
        cliente = Cliente.objects.create(
            nombre="Carlos",
            apellido="Ramírez",
            telefono="3123456789"
        )

        tecnico = Empleado.objects.create(
            cedula=1234567890,
            nombre="Juan",
            apellidos="Pérez",
            fecha_ingreso=date(2024, 1, 10),
            fecha_nacimiento=date(1990, 5, 20),
            celular=3216549870,
            cargo="técnico",  
            salario=2500000,
            estado="Activo"  
        )

        reparacion = Reparacion.objects.create(
            cliente=cliente,
            marca_reloj="Casio",
            descripcion="Cambio de batería",
            codigo_orden=1001,
            fecha_entrega_estimada=date.today(),
            precio=45000,
            espacio_fisico="A1",
            estado="cotización",
            tecnico=tecnico
        )

        self.assertIsNotNone(reparacion.id)
        self.assertEqual(reparacion.marca_reloj, "Casio")
        self.assertEqual(reparacion.cliente.nombre, "Carlos")
