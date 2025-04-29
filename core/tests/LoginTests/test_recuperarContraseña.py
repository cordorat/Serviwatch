from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from django.contrib.auth import get_user_model
from core.forms.recuperar_contraseña_form import recuperarContrasenaForm
from django.core import mail
from unittest.mock import patch

class RecuperarContrasenaFormTest(TestCase):

    def test_form_valid(self):
        form = recuperarContrasenaForm(data = {
            'usuario': 'usuarioValido',
            'email': 'usuario@dominio.com',
        })
        self.assertTrue(form.is_valid())

    def test_username_too_short(self):
        form = recuperarContrasenaForm(data = {
            'usuario': 'usr',
            'email': 'usuario@dominio.com',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['usuario'][0], 'El usuario debe tener entre 8 y 20 caracteres')

    def test_username_too_long(self):
        form = recuperarContrasenaForm(data = {
            'usuario': 'usuarioConNombreMuyLargo',
            'email': 'usuario@dominio.com',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['usuario'][0], 'El usuario debe tener entre 8 y 20 caracteres')

    def test_username_invalid_characters(self):
        form = recuperarContrasenaForm(data = {
            'usuario': 'usuario@2025',
            'email': 'usuario@dominio.com',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['usuario'][0], 'El usuario debe contener solo letras.')

    def test_email_invalid_format(self):
        form = recuperarContrasenaForm(data = {
            'usuario': 'usuario@2025',
            'email': 'usuario@dominio',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'][0], 'Debe cumplir con el formato abc@nnn.com/.co')

    def test_email_missing_at_symbol(self):
        form = recuperarContrasenaForm(data = {
            'usuario': 'usuario@2025',
            'email': 'usuario.dominio.com',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'][0], 'Debe cumplir con el formato abc@nnn.com/.co')

class RecuperarContrasenaViewTests(TestCase):
    def setUp(self):
        # Crear un usuario de prueba
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='securepassword123'
        )
        self.url = reverse('recuperar_contraseña')  # Cambia esto si el nombre de la URL es diferente

    def test_get_request(self):
        """Prueba que la vista devuelve un formulario en una solicitud GET."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], recuperarContrasenaForm)

    def test_post_valid_data(self):
        """Prueba que se envía un correo cuando los datos son válidos."""
        response = self.client.post(self.url, {
            'usuario': 'testuser',
            'email': 'testuser@example.com',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.context)
        self.assertEqual(len(mail.outbox), 1)  # Verifica que se envió un correo
        self.assertIn('Recuperación de contraseña', mail.outbox[0].subject)

    def test_post_invalid_user(self):
        """Prueba que se muestra un error si el usuario no existe."""
        response = self.client.post(self.url, {
            'usuario': 'invaliduser',
            'email': 'testuser@example.com',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
        self.assertEqual(response.context['error'], 'Usuario inexistente')

    def test_post_invalid_email(self):
        """Prueba que se muestra un error si el correo no coincide con el usuario."""
        response = self.client.post(self.url, {
            'usuario': 'testuser',
            'email': 'wrongemail@example.com',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
        self.assertEqual(response.context['error'], 'El correo no está asociado a este usuario')

    def test_post_invalid_form(self):
        """Prueba que se muestra un error si el formulario es inválido."""
        response = self.client.post(self.url, {
            'usuario': '',  # Usuario vacío
            'email': 'invalidemail',  # Email inválido
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
        self.assertEqual(response.context['error'], 'formulario invalido')