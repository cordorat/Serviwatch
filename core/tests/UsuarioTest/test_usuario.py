from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from core.services.usuario_service import crear_usuario
from core.forms.usuario_form import FormularioRegistroUsuario

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

class FormularioRegistroUsuarioTest(TestCase):

    def test_formulario_usuario_exitoso(self):
        form_data = {
            'username': 'Juan1234',
            'password1': 'Sara2345@',
            'password2': 'Sara2345@',
            'email': 'juan@juan.com'
        }
        form = FormularioRegistroUsuario(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, 'Juan1234')
        self.assertEqual(user.email, 'juan@juan.com')
        self.assertTrue(user.check_password('Sara2345@'))
    
    from django.test import TestCase
from core.forms.usuario_form import FormularioRegistroUsuario

class FormularioRegistroUsuarioTest(TestCase):

    def test_formulario_valido(self):
        form_data = {
            'username': 'UsuarioTest',
            'email': 'correo@ejemplo.com',
            'password1': 'Contrasena123!',
            'password2': 'Contrasena123!',
        }
        form = FormularioRegistroUsuario(data=form_data)
        self.assertTrue(form.is_valid())

    def test_passwords_no_coinciden(self):
        form_data = {
            'username': 'UsuarioTest',
            'email': 'correo@ejemplo.com',
            'password1': 'Contrasena123!',
            'password2': 'Otra123!',
        }
        form = FormularioRegistroUsuario(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_contrasena_corta(self):
        form_data = {
            'username': 'Juan123',
            'email': 'juan@correo.com',
            'password1': 'S234@',
            'password2': 'S234@',
        }
        form = FormularioRegistroUsuario(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
        self.assertIn('La contraseña debe tener al menos 8 caracteres.', form.errors['password1'])
    
    def test_contrasena_falta_mayuscula(self):
        form_data = {
            'username': 'Juan1234',
            'email': 'juan@juan.com',
            'password1': 'sara2345@',
            'password2': 'sara2345@',
        }
        form = FormularioRegistroUsuario(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
        self.assertIn('La contraseña debe incluir al menos una letra mayúscula.', form.errors['password1'])

    def test_contrasena_falta_minuscula(self):
        form_data = {
            'username': 'Juan1234',
            'email': 'juan@juan.com',
            'password1': 'SARA2345@',
            'password2': 'SARA2345@',
        }
        form = FormularioRegistroUsuario(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
        self.assertIn('La contraseña debe incluir al menos una letra minúscula.', form.errors['password1'])

    def test_contrasena_falta_numero(self):
        form_data = {
            'username': 'Juan1234',
            'email': 'juan@juan.com',
            'password1': 'Saranoes@',
            'password2': 'Saranoes@',
        }
        form = FormularioRegistroUsuario(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
        self.assertIn('La contraseña debe incluir al menos un número.', form.errors['password1'])
    

    def test_contrasena_igual_a_username(self):
        form_data = {
            'username': 'Juan1234',
            'email': 'juan@correo.com',
            'password1': 'Juan1234!',
            'password2': 'Juan1234!',
        }
        form = FormularioRegistroUsuario(data=form_data)
        self.assertFalse(form.is_valid())
        errores = form.errors.get('password1', []) + form.errors.get('password2', [])
        self.assertIn('La contraseña no puede ser igual al nombre de usuario.', errores)

    def test_contrasena_sin_numeros(self):
        form_data = {
            'username': 'Juan1234',
            'email': 'juan@correo.com',
            'password1': 'Saranoes@',
            'password2': 'Saranoes@',
        }
        form = FormularioRegistroUsuario(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('La contraseña debe incluir al menos un número.', form.errors['password1'])

    def test_contrasena_sin_caracter_especial(self):
        form_data = {
            'username': 'Juan1234',
            'email': 'juan@correo.com',
            'password1': 'Sara2345',
            'password2': 'Sara2345',
        }
        form = FormularioRegistroUsuario(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('La contraseña debe incluir al menos un carácter especial.', form.errors['password1'])

    def test_username_corto(self):
        form_data = {
            'username': 'Juan',
            'email': 'juan@juan.com',
            'password1': 'Sara2345@',
            'password2': 'Sara2345@',
        }
        form = FormularioRegistroUsuario(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('El nombre de usuario debe tener al menos 8 caracteres.', form.errors['username'])