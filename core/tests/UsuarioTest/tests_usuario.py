from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from core.services.usuario_service import crear_usuario
from core.forms.usuario_form import FormularioRegistroUsuario
from django.contrib.messages import get_messages

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

    class UsuarioListViewTest(TestCase):
        def setUp(self):
            self.client = Client()
            self.user = User.objects.create_user(username='testuser', password='testpass')
            self.url = reverse('usuario_list') 

        def test_usuario_list_view_autenticado(self):
            self.client.login(username='testuser', password='testpass')
            response = self.client.get(self.url)

            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'usuario/usuario_list.html')
            self.assertIn('usuarios', response.context)
            self.assertContains(response, 'testuser')  

        def test_usuario_list_view_no_autenticado(self):
            response = self.client.get(self.url)
            self.assertNotEqual(response.status_code, 200)
            self.assertRedirects(response, f'/accounts/login/?next={self.url}')

class UsuarioDeleteViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Usuario autenticado
        self.auth_user = User.objects.create_user(username='authuser', password='12345')
        self.client.force_login(self.auth_user)

        # Usuario que será eliminado
        self.user_to_delete = User.objects.create_user(username='tobedeleted', password='abc123')
        self.delete_url = reverse('usuario_delete', args=[self.user_to_delete.pk])
        self.list_url = reverse('usuario_list')

    def test_delete_existing_user_post(self):
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, self.list_url)
        self.assertFalse(User.objects.filter(pk=self.user_to_delete.pk).exists())

    def test_delete_nonexistent_user(self):
        invalid_url = reverse('usuario_delete', args=[9999])  # Un ID que no existe
        response = self.client.post(invalid_url)
        self.assertRedirects(response, self.list_url)

    def test_get_request_redirects_without_deletion(self):
        response = self.client.get(self.delete_url)
        self.assertRedirects(response, self.list_url)
        self.assertTrue(User.objects.filter(pk=self.user_to_delete.pk).exists())

class UsuarioUpdateViewTests(TestCase):
    def setUp(self):
        self.user_admin = User.objects.create_user(username='admin', password='adminpass')
        self.client.login(username='admin', password='adminpass')

        self.user_to_edit = User.objects.create_user(username='jdoe', email='jdoe@example.com', password='password123')
        self.url = reverse('usuario_update', args=[self.user_to_edit.pk])
        self.list_url = reverse('usuario_list')

    def test_get_request_renders_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuario/usuario_form.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['modo'], 'editar')

    def test_post_valid_data_updates_user_and_redirects(self):
        data = {
            'username': 'johndoe_updated',
            'email': 'newemail@example.com',
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, self.list_url)

        self.user_to_edit.refresh_from_db()
        self.assertEqual(self.user_to_edit.username, 'johndoe_updated')
        self.assertEqual(self.user_to_edit.email, 'newemail@example.com')

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("éxito" in str(m.message).lower() for m in messages))

    def test_post_invalid_data_shows_error(self):
        data = {
            'username': '', 
            'email': 'correo@valido.com',
            }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuario/usuario_form.html')

        self.assertFormError(response.context['form'], 'username', 'Este campo es obligatorio.')

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("error" in str(m.message).lower() for m in messages))

    def test_user_does_not_exist_redirects_and_shows_message(self):
        url = reverse('usuario_update', args=[99999]) 
        response = self.client.get(url)
        self.assertRedirects(response, self.list_url)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("no existe" in str(m.message).lower() for m in messages))