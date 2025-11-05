from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.forms.usuario_form import FormularioRegistroUsuario, FormularioEditarUsuario
import json

class UsuarioViewTests(TestCase):

    def setUp(self):
        # Crear un usuario admin para login
        self.admin = User.objects.create_user(username='adminuser', password='AdminPass123!')
        self.admin.is_staff = True
        self.admin.save()

        self.client = Client()
        self.client.login(username='adminuser', password='AdminPass123!')

        # Crear usuario para editar y eliminar
        self.usuario = User.objects.create_user(username='usuario1', email='user1@example.com', password='Password123!')

    def test_usuario_list_view_get(self):
        url = reverse('usuario_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('usuarios', response.context)
        # Comprobar que usuario listado no tiene superusers
        for u in response.context['usuarios']:
            self.assertFalse(u.is_superuser)

    def test_usuario_create_view_get(self):
        url = reverse('usuario_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], FormularioRegistroUsuario)
        self.assertFalse(response.context['success'])

    def test_usuario_create_view_get_success_param(self):
        url = reverse('usuario_create') + '?success=true'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['success'])

    def test_usuario_create_view_post_valid(self):
        url = reverse('usuario_create')
        data = {
            'username': 'nuevo_usuario',
            'email': 'nuevo@example.com',
            'password1': 'ValidPass123!',
            'password2': 'ValidPass123!'
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('usuario_list'))
        self.assertTrue(User.objects.filter(username='nuevo_usuario').exists())


    def test_usuario_create_view_post_ajax_valid(self):
        url = reverse('usuario_create')
        data = {
            'username': 'ajax_user',
            'email': 'ajax@example.com',
            'password1': 'ValidPass123!',
            'password2': 'ValidPass123!'
        }
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content['success'])
        self.assertTrue(User.objects.filter(username='ajax_user').exists())

    def test_usuario_create_view_post_ajax_invalid(self):
        url = reverse('usuario_create')
        data = {
            'username': 'short',
            'email': 'invalid',
            'password1': 'pass',
            'password2': 'diff'
        }
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertFalse(content['success'])
        self.assertIn('username', content['errors'])
        self.assertIn('email', content['errors'])
        self.assertIn('password2', content['errors'])

    def test_usuario_update_view_get(self):
        url = reverse('usuario_update', kwargs={'pk': self.usuario.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], FormularioEditarUsuario)
        self.assertEqual(response.context['modo'], 'editar')

    def test_usuario_update_view_post_valid(self):
        url = reverse('usuario_update', kwargs={'pk': self.usuario.pk})
        data = {
            'username': 'usuario_editado',
            'email': 'editado@example.com'
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('usuario_list'))
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.username, 'usuario_editado')
        self.assertEqual(self.usuario.email, 'editado@example.com')


    def test_usuario_update_view_post_ajax_valid(self):
        url = reverse('usuario_update', kwargs={'pk': self.usuario.pk})
        data = {
            'username': 'usuario_ajax',
            'email': 'ajaxedit@example.com'
        }
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content['success'])
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.username, 'usuario_ajax')

    def test_usuario_update_view_post_ajax_invalid(self):
        url = reverse('usuario_update', kwargs={'pk': self.usuario.pk})
        data = {
            'username': '',
            'email': 'invalidemail'
        }
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertFalse(content['success'])
        self.assertIn('username', content['errors'])
        self.assertIn('email', content['errors'])

    def test_usuario_update_view_nonexistent_user(self):
        url = reverse('usuario_update', kwargs={'pk': 99999})
        response = self.client.get(url)
        # Debe redirigir a lista con mensaje error
        self.assertRedirects(response, reverse('usuario_list'))

    def test_usuario_delete_view_post(self):
        url = reverse('usuario_delete', kwargs={'pk': self.usuario.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('usuario_list'))
        self.assertFalse(User.objects.filter(pk=self.usuario.pk).exists())

    def test_usuario_delete_view_post_ajax(self):
        url = reverse('usuario_delete', kwargs={'pk': self.usuario.pk})
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content['success'])
        self.assertFalse(User.objects.filter(pk=self.usuario.pk).exists())

    def test_usuario_delete_view_nonexistent(self):
        url = reverse('usuario_delete', kwargs={'pk': 999999})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('usuario_list'))

    def test_usuario_delete_view_nonexistent_ajax(self):
        url = reverse('usuario_delete', kwargs={'pk': 999999})
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)
        content = json.loads(response.content)
        self.assertFalse(content['success'])

    def test_usuario_delete_view_get_ajax_method_not_allowed(self):
        url = reverse('usuario_delete', kwargs={'pk': self.usuario.pk})
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 405)
        content = json.loads(response.content)
        self.assertFalse(content['success'])

    def test_usuario_delete_view_get_normal_redirect(self):
        url = reverse('usuario_delete', kwargs={'pk': self.usuario.pk})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('usuario_list'))
