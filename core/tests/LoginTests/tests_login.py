from django.test import TestCase, Client
from django.urls import reverse
from core.forms.login_form import LoginForm
from django.contrib.auth import get_user_model

class LoginFormTest(TestCase):
    def test_loginform_valido(self):
        form = LoginForm(data={
            'usuario': 'lucasPrueba',
            'contraseña': 'lucasPrueba1@'
        })
        self.assertTrue(form.is_valid())

    def test_loginform_camposVacios(self):
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('usuario', form.errors)
        self.assertIn('contraseña', form.errors)

    def test_loginform_contraseñaSinNumero(self):
        form = LoginForm(data={
            'usuario': 'lucasPrueba',
            'contraseña': 'pruebaaa@'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('contraseña', form.errors)

    def test_loginform_contraseñaSinLetras(self):
        form = LoginForm(data={
            'usuario': 'lucasPrueba',
            'contraseña': '12345678@'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('contraseña', form.errors)

    def test_loginform_contraseñaSinCaracterEspecial(self):
        form = LoginForm(data={
            'usuario': 'lucasPrueba',
            'contraseña': 'prueba1234'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('contraseña', form.errors)

class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('login')
        self.User = get_user_model()

        self.user = self.User.objects.create_user(
            username='usuarioNormal',
            password='contraseña123@'
        )

        self.superuser = self.User.objects.create_superuser(
            username='usuarioAdmin',
            password='contraseña123@' 
        )
        
    def test_loginView_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login/login.html')
        self.assertIn('form', response.context)

    def test_loginView_usuarioInexistente(self):
        response = self.client.post(self.url, {
            'usuario': 'noExiste',
            'contraseña': 'noExiste123@'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuario inexistente')

    def test_loginView_contraseñaIncorrecta(self):
        response = self.client.post(self.url, {
            'usuario': 'usuarioNormal',
            'contraseña': 'contraseñaMala1@'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuario o contraseña incorrectos')

    def test_loginView_redireccionDeUsuario(self):
        response = self.client.post(self.url, {
            'usuario': 'usuarioNormal',
            'contraseña': 'contraseña123@'
        })
        self.assertRedirects(response, reverse('cliente_list'))

    def test_loginView_redireccionDeAdmin(self):
        response = self.client.post(self.url, {
            'usuario': 'usuarioAdmin',
            'contraseña': 'contraseña123@'
        })
        self.assertRedirects(response, reverse('cliente_create'))