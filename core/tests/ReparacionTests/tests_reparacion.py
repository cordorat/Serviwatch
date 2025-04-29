from django.test import TestCase
from core.models import Reparacion, Cliente, Empleado
from datetime import date
from core.forms.reparacion_form import ReparacionForm
from core.services.reparacion_service import get_all_reparaciones, crear_reparacion


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
            # Formato correcto para DateField
            'fecha_entrega_estimada': date.today().strftime('%Y-%m-%d'),
            'precio': 45000,  # Número entero positivo
            'espacio_fisico': 'A1',
            'estado': 'cotización',  # Debe coincidir con las opciones de ESTADOS
            'tecnico': self.tecnico.id
        }

        form = ReparacionForm(data=form_data)
        if not form.is_valid():
            print("Errores del formulario:", form.errors)
            # Para ver qué datos pasaron la validación
            print("Data limpia:", form.cleaned_data)
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


class ReparacionServiceTest(TestCase):
    def setUp(self):
        # Crear cliente
        self.cliente = Cliente.objects.create(
            nombre="Carlos",
            apellido="Ramírez",
            telefono="3123456789"
        )

        # Crear técnico
        self.tecnico = Empleado.objects.create(
            cedula="1234567890",
            nombre="Juan",
            apellidos="Pérez",
            fecha_ingreso="2024-01-10",
            fecha_nacimiento="1990-05-20",
            celular="3216549870",
            cargo="Técnico",
            salario=2500000,
            estado="Activo"
        )

        # Crear reparación de prueba
        self.reparacion = Reparacion.objects.create(
            cliente=self.cliente,
            marca_reloj="Casio",
            descripcion="Cambio de batería",
            codigo_orden="1001",
            fecha_entrega_estimada=date.today(),
            precio=45000,
            espacio_fisico="A1",
            estado="cotización",
            tecnico=self.tecnico
        )

    def test_get_all_reparaciones(self):
        """Prueba que get_all_reparaciones retorne todas las reparaciones"""
        # Obtener reparaciones
        reparaciones = get_all_reparaciones()

        # Verificar que se obtiene la reparación creada
        self.assertEqual(reparaciones.count(), 1)
        self.assertEqual(reparaciones[0], self.reparacion)

    def test_crear_reparacion(self):
        """Prueba que crear_reparacion cree una nueva reparación correctamente"""
        # Datos del formulario
        form_data = {
            'cliente': self.cliente.id,
            'cliente_nombre': self.cliente.nombre,
            'celular_cliente': self.cliente.telefono,
            'marca_reloj': 'Rolex',
            'descripcion': 'Limpieza general',
            'codigo_orden': '1002',
            'fecha_entrega_estimada': date.today(),
            'precio': 75000,
            'espacio_fisico': 'B2',
            'estado': 'cotización',
            'tecnico': self.tecnico.id
        }

        # Crear formulario
        form = ReparacionForm(data=form_data)

        if not form.is_valid():
            print("Cleaned data:", form.cleaned_data)  # Added for debugging
            print("All errors:", form.errors.as_json())

        # Verificar que el formulario es válido
        self.assertTrue(form.is_valid(),
                        f"Errores del formulario: {form.errors}")

        # Crear reparación
        nueva_reparacion = crear_reparacion(form)

        # Verificar que la reparación se creó correctamente
        self.assertIsNotNone(nueva_reparacion.id)
        self.assertEqual(nueva_reparacion.marca_reloj, 'Rolex')
        self.assertEqual(nueva_reparacion.cliente, self.cliente)
        self.assertEqual(nueva_reparacion.tecnico, self.tecnico)

    def test_get_all_reparaciones_empty(self):
        """Prueba que get_all_reparaciones funcione con base de datos vacía"""
        # Limpiar base de datos
        Reparacion.objects.all().delete()

        # Verificar que retorna queryset vacío
        reparaciones = get_all_reparaciones()
        self.assertEqual(reparaciones.count(), 0)

    def test_crear_reparacion_invalid_form(self):
        """Prueba que crear_reparacion maneje formularios inválidos"""
        form = ReparacionForm(data={})  # Formulario vacío

        # Verificar que el formulario es inválido
        self.assertFalse(form.is_valid())

        # Intentar crear reparación con formulario inválido
        with self.assertRaises(ValueError):
            crear_reparacion(form)
