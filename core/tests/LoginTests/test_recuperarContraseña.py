from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from django.contrib.auth import get_user_model
from core.forms.recuperar_contraseña_form import recuperarContrasenaForm, CambiarContrasenaForm
from core.models import PasswordResetToken
from django.core import mail
from unittest.mock import patch
from django.utils.crypto import get_random_string
from django.utils import timezone
import datetime

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


# tests de cambiar contraseña

class CambiarContrasenaFormTest(TestCase):

    def test_form_valid(self):
        form = CambiarContrasenaForm(data={
            'password': 'NuevaContraseña1!',
            'confirm_password': 'NuevaContraseña1!',
        })
        self.assertTrue(form.is_valid())

    def test_password_too_short(self):
        form = CambiarContrasenaForm(data={
            'password': 'Corta1!',
            'confirm_password': 'Corta1!',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password'][0], 'La contraseña debe tener entre 8 y 20 caracteres')

    def test_password_too_long(self):
        form = CambiarContrasenaForm(data={
            'password': 'MuyLargaContraseña1234567890!',
            'confirm_password': 'MuyLargaContraseña1234567890!',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password'][0], 'La contraseña debe tener entre 8 y 20 caracteres')

    def test_password_missing_uppercase(self):
        form = CambiarContrasenaForm(data={
            'password': 'nuevacontraseña1!',
            'confirm_password': 'nuevacontraseña1!',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password'][0], 'La contraseña debe contener al menos una letra mayúscula')

    def test_password_missing_lowercase(self):
        form = CambiarContrasenaForm(data={
            'password': 'NUEVACONTRASEÑA1!',
            'confirm_password': 'NUEVACONTRASEÑA1!',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password'][0], 'La contraseña debe contener al menos una letra minúscula')

    def test_password_missing_number(self):
        form = CambiarContrasenaForm(data={
            'password': 'NuevaContraseña!',
            'confirm_password': 'NuevaContraseña!',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password'][0], 'La contraseña debe contener al menos un número')

    def test_password_missing_special_char(self):
        form = CambiarContrasenaForm(data={
            'password': 'NuevaContraseña1',
            'confirm_password': 'NuevaContraseña1',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password'][0], 'La contraseña debe contener al menos un carácter especial')

    def test_passwords_do_not_match(self):
        form = CambiarContrasenaForm(data={
            'password': 'NuevaContraseña1!',
            'confirm_password': 'OtraContraseña1!',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['confirm_password'][0], 'Las contraseñas no coinciden')


class CambiarContrasenaViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='OldPassword1!'
        )
        self.token = get_random_string(length=32)
        self.reset_token = PasswordResetToken.objects.create(
            user=self.user,
            token=self.token
        )
        self.url = reverse('cambiar_contraseña', kwargs={'token': self.token})

    def test_get_request_renders_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login/cambiar_contraseña.html')
        self.assertIsInstance(response.context['form'], CambiarContrasenaForm)

    def test_post_valid_data_changes_password(self):
        response = self.client.post(self.url, {
            'password': 'NewValid1!',
            'confirm_password': 'NewValid1!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '¡Contraseña cambiada con éxito!')

        # Verifica que la contraseña se haya actualizado
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewValid1!'))

    def test_post_invalid_form_shows_error(self):
        response = self.client.post(self.url, {
            'password': '123',
            'confirm_password': '123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Formulario inválido')

    def test_expired_token_renders_expired_template(self):
        self.reset_token.used = True
        self.reset_token.save()
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'login/token_expirado.html')

    def test_invalid_token_renders_invalid_template(self):
        invalid_url = reverse('cambiar_contraseña', kwargs={'token': 'invalidtoken123'})
        response = self.client.get(invalid_url)
        self.assertTemplateUsed(response, 'login/token_invalido.html')


class PasswordResetTokenTest(TestCase):

    def setUp(self):
        # Crear un usuario de prueba
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='securepassword123'
        )
        # Crear un token para la recuperación de contraseña
        self.token = PasswordResetToken.objects.create(
            user=self.user,
            token='validtoken123'
        )

    def test_is_valid_token_not_expired(self):
        """Prueba que el token sea válido si no ha expirado y no ha sido usado."""
        self.assertTrue(self.token.is_valid())

    def test_is_invalid_token_used(self):
        """Prueba que el token sea inválido si ya ha sido usado."""
        self.token.used = True
        self.token.save()
        self.assertFalse(self.token.is_valid())

    def test_is_invalid_token_expired(self):
        """Prueba que el token sea inválido si ha expirado."""
        self.token.created_at = timezone.now() - datetime.timedelta(days=2)  # Más de 24 horas
        self.token.save()
        self.assertFalse(self.token.is_valid())

    def test_is_valid_token_within_24_hours(self):
        """Prueba que el token sea válido si no ha expirado (dentro de las 24 horas)."""
        self.token.created_at = timezone.now() - datetime.timedelta(hours=1)  # Dentro de 24 horas
        self.token.save()
        self.assertTrue(self.token.is_valid())