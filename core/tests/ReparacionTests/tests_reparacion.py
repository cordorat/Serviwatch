from django.test import TestCase
from core.models import Reparacion, Cliente, Empleado
from datetime import date
from core.forms.reparacion_form import ReparacionForm


class ReparacionModelTest(TestCase):
    def test_crear_reparacion(self):
        cliente = Cliente.objects.create(
            nombre="Carlos",
            apellido="Ramírez",
            telefono="3123456789"
        )

        tecnico = Empleado.objects.create(
            cedula="1234567890",
            nombre="Juan",
            apellidos="Pérez",
            fecha_ingreso=date(2024, 1, 10),
            fecha_nacimiento=date(1990, 5, 20),
            celular="3216549870",
            cargo="técnico",
            salario="2500000",
            estado="Activo"
        )

        reparacion = Reparacion.objects.create(
            cliente=cliente,
            marca_reloj="Casio",
            descripcion="Cambio de batería",
            codigo_orden="1001",
            fecha_entrega_estimada=date.today(),
            precio=45000,
            espacio_fisico="A1",
            estado="cotización",
            tecnico=tecnico
        )

        self.assertIsNotNone(reparacion.id)
        self.assertEqual(reparacion.marca_reloj, "Casio")
        self.assertEqual(reparacion.cliente.nombre, "Carlos")


class ReparacionFormTest(TestCase):
    def setUp(self):
        # Crear el cliente y técnico que se usarán en todas las pruebas
        self.cliente = Cliente.objects.create(
            nombre="Carlos",
            apellido="Ramírez",
            telefono="3123456789"  # Exactamente 10 dígitos
        )

        self.tecnico = Empleado.objects.create(
            cedula="1234567890",
            nombre="Juan",
            apellidos="Pérez",
            fecha_ingreso=date(2024, 1, 10),
            fecha_nacimiento=date(1990, 5, 20),
            celular="3216549870",
            cargo="Técnico",
            salario="2500000",
            estado="Activo"
        )

    def test_reparacion_form(self):
        form_data = {
            'cliente': self.cliente.id,
            'cliente_nombre': self.cliente.nombre,  # Solo el nombre sin apellido
            'celular_cliente': self.cliente.telefono,  # Debe coincidir exactamente
            'marca_reloj': 'Casio',
            'descripcion': 'Cambio de batería',
            'codigo_orden': '1001',  # Debe ser único
            'fecha_entrega_estimada': date.today().strftime('%Y-%m-%d'),  # Formato correcto para DateField
            'precio': 45000,  # Número entero positivo
            'espacio_fisico': 'A1',
            'estado': 'cotización',  # Debe coincidir con las opciones de ESTADOS
            'tecnico': self.tecnico.id
        }

        form = ReparacionForm(data=form_data)
        if not form.is_valid():
            print("Errores del formulario:", form.errors)
            print("Data limpia:", form.cleaned_data)  # Para ver qué datos pasaron la validación
        self.assertTrue(form.is_valid())
    
    def test_reparacion_form_invalid(self):
        form_data = {
            'marca_reloj': '',
            'descripcion': '',
            'codigo_orden': '',
            'fecha_entrega_estimada': '',
            'precio': '',
            'espacio_fisico': '',
            'estado': '',
        }

        form = ReparacionForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_celular_cliente_invalido(self):
        form_data = {
            'celular_cliente': 'abc123',
            'cliente_nombre': 'Carlos'
        }
        form = ReparacionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('celular_cliente', form.errors)
        self.assertEqual(form.errors['celular_cliente']
                         [0], "El celular solo debe contener números.")

    def test_codigo_orden_invalido(self):
        form_data = {
            'codigo_orden': 'ABC123',
            'cliente_nombre': 'Carlos',
            'celular_cliente': '3123456789'
        }
        form = ReparacionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('codigo_orden', form.errors)
        self.assertEqual(form.errors['codigo_orden']
                         [0], "El código de orden debe ser numérico.")

    def test_precio_invalido(self):
        form_data = {
            'precio': 'abc',
            'cliente_nombre': 'Carlos',
            'celular_cliente': '3123456789'
        }
        form = ReparacionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('precio', form.errors)
        self.assertEqual(form.errors['precio'][0],
                         "El precio debe ser un número.")

    def test_espacio_fisico_muy_largo(self):
        form_data = {
            'espacio_fisico': 'A' * 16,  # 16 caracteres
            'cliente_nombre': 'Carlos',
            'celular_cliente': '3123456789'
        }
        form = ReparacionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('espacio_fisico', form.errors)
        self.assertEqual(form.errors['espacio_fisico'][0],
                         "El espacio físico no puede tener más de 15 caracteres.")

    def test_marca_reloj_muy_larga(self):
        form_data = {
            'marca_reloj': 'M' * 31,  # 31 caracteres
            'cliente_nombre': 'Carlos',
            'celular_cliente': '3123456789'
        }
        form = ReparacionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('marca_reloj', form.errors)
        self.assertEqual(form.errors['marca_reloj'][0],
                         "La marca del reloj no puede superar los 30 caracteres.")

    def test_descripcion_muy_larga(self):
        form_data = {
            'descripcion': 'D' * 501,  # 501 caracteres
            'cliente_nombre': 'Carlos',
            'celular_cliente': '3123456789'
        }
        form = ReparacionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('descripcion', form.errors)
        self.assertEqual(form.errors['descripcion'][0],
                         "La descripción no puede superar los 500 caracteres.")

    def test_cliente_no_existe(self):
        form_data = {
            'cliente_nombre': 'Cliente Inexistente',
            'celular_cliente': '3123456789',
            'marca_reloj': 'Casio',
            'descripcion': 'Cambio de batería',
            'codigo_orden': '1001',
            'fecha_entrega_estimada': date.today(),
            'precio': '45000',
            'espacio_fisico': 'A1',
            'estado': 'cotización',
            'tecnico': self.tecnico.id
        }
        form = ReparacionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            str(form.errors['__all__'][0]),
            "No se encontró un cliente con ese nombre y celular."
        )

    def test_precio_invalido(self):
        # Test con texto
        form_data = {
            'precio': 'abc',
            'cliente_nombre': 'Carlos',
            'celular_cliente': '3123456789'
        }
        form = ReparacionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('precio', form.errors)
        self.assertEqual(
            form.errors['precio'][0],
            "El precio debe ser un número entero."
        )

        # Test con número negativo
        form_data['precio'] = -1000
        form = ReparacionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('precio', form.errors)
        self.assertEqual(
            form.errors['precio'][0],
            "El precio debe ser mayor a 0."
        )
