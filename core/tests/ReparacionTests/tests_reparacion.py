from django.test import TestCase
from core.models import Reparacion, Cliente, Empleado
from datetime import date, timedelta
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
        self.cliente = Cliente.objects.create(
            nombre="Test",
            apellido="User",
            telefono="1234567890"
        )
        self.tecnico = Empleado.objects.create(
            cedula="1234567890",
            nombre="Tech",
            apellidos="Support",
            fecha_ingreso=date.today(),
            fecha_nacimiento=date(1990, 5, 20),
            celular="3216549870",
            cargo="Técnico",
            salario=2500000,
            estado="Activo"
        )

        self.valid_data = {
            'cliente': self.cliente,
            'marca_reloj': "Rolex",
            'descripcion': "Reparación de cristal y ajuste de hora",
            'codigo_orden': "12345",
            'fecha_entrega_estimada': date(2025, 4, 30),
            'precio': 100,
            'espacio_fisico': "Caja 1",
            'estado': "Reparación",
            'tecnico': self.tecnico
        }

    def test_valid_form(self):
        form = ReparacionForm(data=self.valid_data)
        if not form.is_valid():
            print("\nForm Validation Errors:")
            for field, errors in form.errors.items():
                print(f"{field}: {errors}")
            print("\nSubmitted Data:")
            for key, value in self.valid_data.items():
                print(f"{key}: {value}")
            print("\nCleaned Data:")
            print(form.cleaned_data if hasattr(
                form, 'cleaned_data') else "No cleaned data")

        self.assertTrue(form.is_valid(),
                        msg=f"Form validation failed: {form.errors}")

    def test_codigo_orden_numerico(self):
        self.valid_data['codigo_orden'] = "ABC123"
        form = ReparacionForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('codigo_orden', form.errors)

    def test_precio_positivo(self):
        self.valid_data['precio'] = -100
        form = ReparacionForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('precio', form.errors)

    def test_descripcion_minima(self):
        self.valid_data['descripcion'] = "Corto"
        form = ReparacionForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('descripcion', form.errors)

    def test_fecha_futura(self):
        self.valid_data['fecha_entrega_estimada'] = (
            date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        form = ReparacionForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_entrega_estimada', form.errors)

    def test_codigo_orden_unico(self):
        Reparacion.objects.create(**self.valid_data)
        form = ReparacionForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('codigo_orden', form.errors)


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
            'estado': 'Cotización',
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
