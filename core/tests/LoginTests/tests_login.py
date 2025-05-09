from django.test import TestCase, Client
from django.urls import reverse
from core.forms.login_form import LoginForm
from django.contrib.auth import get_user_model

class LoginFormTest(TestCase):
    def test_loginform_valido(self):
        form = LoginForm(data={
            'usuario': 'lucasPrueba',
            'contrasenia': 'lucasPrueba1@'
        })
        self.assertTrue(form.is_valid())

    def test_loginform_camposVacios(self):
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('usuario', form.errors)
        self.assertIn('contrasenia', form.errors)

    def test_loginform_contraseniaSinNumero(self):
        form = LoginForm(data={
            'usuario': 'lucasPrueba',
            'contrasenia': 'pruebaaa@'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('contrasenia', form.errors)

    def test_loginform_contraseniaSinLetras(self):
        form = LoginForm(data={
            'usuario': 'lucasPrueba',
            'contrasenia': '12345678@'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('contrasenia', form.errors)

    def test_loginform_contraseniaSinCaracterEspecial(self):
        form = LoginForm(data={
            'usuario': 'lucasPrueba',
            'contrasenia': 'prueba1234'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('contrasenia', form.errors)

class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('login')
        self.User = get_user_model()

        self.user = self.User.objects.create_user(
            username='usuarioNormal',
            password='contrasenia123@'
        )

        self.superuser = self.User.objects.create_superuser(
            username='usuarioAdmin',
            password='contrasenia123@' 
        )
        
    def test_loginView_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login/login.html')
        self.assertIn('form', response.context)

    def test_loginView_usuarioInexistente(self):
        response = self.client.post(self.url, {
            'usuario': 'noExiste',
            'contrasenia': 'noExiste123@'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuario inexistente')

    def test_loginView_contraseniaIncorrecta(self):
        response = self.client.post(self.url, {
            'usuario': 'usuarioNormal',
            'contrasenia': 'contraseniaMala1@'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuario o contraseña incorrectos')

    def test_loginView_redireccionDeUsuario(self):
        response = self.client.post(self.url, {
            'usuario': 'usuarioNormal',
            'contrasenia': 'contrasenia123@'
        })
        self.assertRedirects(response, reverse('cliente_list'))

    def test_loginView_redireccionDeAdmin(self):
        response = self.client.post(self.url, {
            'usuario': 'usuarioAdmin',
            'contrasenia': 'contrasenia123@'
        })
        self.assertRedirects(response, reverse('usuario_list'))