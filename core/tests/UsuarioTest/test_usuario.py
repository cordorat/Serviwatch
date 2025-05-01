from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from core.services.usuario_service import crear_usuario

class GuardarUsuarioServiceTest(TestCase):

    def test_guardar_usuario_exitosamente(self):
        user = crear_usuario("Juan1234", "Sara2345@", "juan@juan.com")
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, "Juan1234")
        self.assertEqual(user.email, "juan@juan.com")
        self.assertTrue(user.check_password("Sara2345@"))

    def test_guardar_usuario_username_existente(self):
        crear_usuario("Juan1234", "Sara2345@", "juan@juan.com")
        with self.assertRaisesMessage(ValidationError, "El nombre de usuario ya existe."):
            crear_usuario("Juan1234", "Maria90@", "otro@ejemplo.com")

    def test_guardar_usuario_email_existente(self):
        crear_usuario("Juan1234", "Sara2345@", "juan@juan.com")
        with self.assertRaisesMessage(ValidationError, "El correo electrónico ya está en uso."):
            crear_usuario("usuario2", "Nad@8902", "juan@juan.com")
