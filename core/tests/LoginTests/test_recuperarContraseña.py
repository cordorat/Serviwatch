from django.test import TestCase
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model
from core.forms.recuperar_contraseña_form import recuperarContrasenaForm, CambiarContrasenaForm
from core.models import PasswordResetToken
from django.utils.crypto import get_random_string
from django.utils import timezone
from unittest.mock import patch
from core.services.recuperar_service import get_user_by_username, is_email_matching, generate_password_reset_token, build_reset_url, send_password_reset_email, get_token, update_user_password, mark_token_as_used
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


class TestRecuperacionService:
    def user(self):
        return get_user_model().objects.create_user(username='testuser', email='test@example.com', password='password123')

    def test_get_user_by_username_found(self, user):
        result, error = service.get_user_by_username('testuser')
        assert result == user
        assert error is None

    def test_get_user_by_username_not_found(self):
        result, error = service.get_user_by_username('nonexistent')
        assert result is None
        assert error == "Usuario inexistente"

    def test_is_email_matching_true(self, user):
        assert service.is_email_matching(user, 'test@example.com') is True

    def test_is_email_matching_false(self, user):
        assert service.is_email_matching(user, 'wrong@example.com') is False

    def test_generate_password_reset_token_creates_token(self, user):
        token = service.generate_password_reset_token(user)
        assert isinstance(token, str)
        assert PasswordResetToken.objects.filter(user=user, token=token).exists()

    def test_get_token_valid(self, user):
        token_str = service.generate_password_reset_token(user)
        token_obj, error = service.get_token(token_str)
        assert token_obj is not None
        assert error is None

    def test_get_token_invalid(self):
        token_obj, error = service.get_token('nonexistenttoken')
        assert token_obj is None
        assert error == 'Token inválido'

    def test_get_token_expired(self, user):
        token_str = service.generate_password_reset_token(user)
        token_obj = PasswordResetToken.objects.get(token=token_str)
        token_obj.created_at = timezone.now() - timezone.timedelta(hours=25)
        token_obj.save()
        result, error = service.get_token(token_str)
        assert result is None
        assert error == 'Token expirado'

    def test_update_user_password_changes_password(self, user):
        service.update_user_password(user, 'newpassword123')
        assert user.check_password('newpassword123')

    def test_mark_token_as_used_sets_flag(self, user):
        token_str = service.generate_password_reset_token(user)
        token_obj = PasswordResetToken.objects.get(token=token_str)
        service.mark_token_as_used(token_obj)
        token_obj.refresh_from_db()
        assert token_obj.used is True

    @patch('core.services.recuperacion_service.send_mail')
    def test_send_password_reset_email_sends_email(self, mock_send_mail):
        url = "http://example.com/reset"
        service.send_password_reset_email('test@example.com', url)
        mock_send_mail.assert_called_once()
        assert 'test@example.com' in mock_send_mail.call_args[1]['recipient_list']

class RecuperarContrasenaViewTests(TestCase):

    def setUp(self):
        # Crear un usuario de prueba
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='securepassword123'
        )
        self.url = reverse('recuperar_contraseña') 

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
        self.assertEqual(response.context['error'], 'Formulario inválido')


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
        """Prueba que la vista renderiza el formulario con el token."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login/cambiar_contraseña.html')
        self.assertIsInstance(response.context['form'], CambiarContrasenaForm)

    def test_post_valid_data_changes_password(self):
        """Prueba que se cambia la contraseña correctamente si los datos son válidos."""
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
        """Prueba que muestra un error si el formulario es inválido."""
        response = self.client.post(self.url, {
            'password': '123',
            'confirm_password': '123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Formulario inválido')

    def test_expired_token_renders_expired_template(self):
        """Prueba que muestra la plantilla de token expirado si el token ya se ha usado."""
        self.reset_token.used = True
        self.reset_token.save()
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'login/token_expirado.html')

    def test_invalid_token_renders_invalid_template(self):
        """Prueba que muestra la plantilla de token inválido si el token es incorrecto."""
        invalid_url = reverse('cambiar_contraseña', kwargs={'token': 'invalidtoken123'})
        response = self.client.get(invalid_url)
        self.assertTemplateUsed(response, 'login/token_invalido.html')
