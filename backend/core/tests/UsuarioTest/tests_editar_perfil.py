from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from core.forms.password_change_form import PasswordChangeForm
from core.services.password_change_service import validate_current_password, validate_new_password, change_password

class PasswordChangeFormTest(TestCase):
    
    def test_form_valid(self):
        form = PasswordChangeForm(data={
            'contrasenia_actual': 'SecurePass1!',
            'contrasenia_nueva': 'NewSecurePass2!',
            'confirmacion_contrasenia': 'NewSecurePass2!'
        })
        self.assertTrue(form.is_valid())
    
    def test_password_too_short(self):
        form = PasswordChangeForm(data={
            'contrasenia_actual': 'SecurePass1!',
            'contrasenia_nueva': 'Short1!',
            'confirmacion_contrasenia': 'Short1!'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['contrasenia_nueva'][0], 'La contraseña debe tener al menos 8 caracteres')
    
    def test_password_too_long(self):
        form = PasswordChangeForm(data={
            'contrasenia_actual': 'SecurePass1!',
            'contrasenia_nueva': 'ThisPasswordIsTooLongForTheSystem123!',
            'confirmacion_contrasenia': 'ThisPasswordIsTooLongForTheSystem123!'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['contrasenia_nueva'][0], 'La contraseña no puede tener más de 16 caracteres')
    
    def test_passwords_dont_match(self):
        form = PasswordChangeForm(data={
            'contrasenia_actual': 'SecurePass1!',
            'contrasenia_nueva': 'NewSecurePass2!',
            'confirmacion_contrasenia': 'DifferentPass3!'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['confirmacion_contrasenia'][0], 'Las contraseñas no coinciden')
    
    def test_new_password_no_letter(self):
        form = PasswordChangeForm(data={
            'contrasenia_actual': 'SecurePass1!',
            'contrasenia_nueva': '12345678!',
            'confirmacion_contrasenia': '12345678!'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['contrasenia_nueva'][0], 'La contraseña debe tener al menos una letra')
    
    def test_new_password_no_number(self):
        form = PasswordChangeForm(data={
            'contrasenia_actual': 'SecurePass1!',
            'contrasenia_nueva': 'SecurePass!',
            'confirmacion_contrasenia': 'SecurePass!'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['contrasenia_nueva'][0], 'La contraseña debe tener al menos un número')
    
    def test_new_password_no_special_char(self):
        form = PasswordChangeForm(data={
            'contrasenia_actual': 'SecurePass1!',
            'contrasenia_nueva': 'SecurePass1',
            'confirmacion_contrasenia': 'SecurePass1'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['contrasenia_nueva'][0], 'La contraseña debe tener al menos un caracter especial')
    
    def test_new_password_same_as_current(self):
        form = PasswordChangeForm(data={
            'contrasenia_actual': 'SecurePass1!',
            'contrasenia_nueva': 'SecurePass1!',
            'confirmacion_contrasenia': 'SecurePass1!'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['contrasenia_nueva'][0], 'La contraseña nueva no puede ser igual a la anterior')


class PasswordChangeServiceTest(TestCase):
    
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='OldPassword1!'
        )
    
    def test_validate_current_password_valid(self):
        is_valid, error = validate_current_password(self.user, 'OldPassword1!')
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_current_password_invalid(self):
        is_valid, error = validate_current_password(self.user, 'WrongPassword!')
        self.assertFalse(is_valid)
        self.assertEqual(error, 'Contraseña incorrecta')
    
    def test_validate_new_password_different(self):
        is_valid, error = validate_new_password('OldPassword1!', 'NewPassword2!')
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_new_password_same(self):
        is_valid, error = validate_new_password('SamePassword1!', 'SamePassword1!')
        self.assertFalse(is_valid)
        self.assertEqual(error, 'Contraseña nueva no puede ser igual a la anterior')
    
    def test_change_password_success(self):
        success, message = change_password(self.user, 'NewPassword2!')
        self.assertTrue(success)
        self.assertEqual(message, 'Su contraseña ha sido actualizada correctamente')
        
        # Verificar que la contraseña se haya actualizado
        self.user.refresh_from_db()
        self.assertTrue(check_password('NewPassword2!', self.user.password))

class PasswordChangeViewTest(TestCase):
    
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='OldPassword1!'
        )
        self.url = reverse('password_change')
        self.client.force_login(self.user)
    
    def test_get_request_renders_form(self):
        """Prueba que la vista renderiza el formulario."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuario/password_change.html')
        self.assertIsInstance(response.context['form'], PasswordChangeForm)
    
    def test_post_valid_data_changes_password(self):
        """Prueba que se cambia la contraseña correctamente si los datos son válidos."""
        response = self.client.post(self.url, {
            'contrasenia_actual': 'OldPassword1!',
            'contrasenia_nueva': 'NewPassword2!',
            'confirmacion_contrasenia': 'NewPassword2!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.context)
        self.assertEqual(response.context['success'], 'Su contraseña ha sido actualizada correctamente')
        
        # Verificar que la contraseña se haya actualizado
        self.user.refresh_from_db()
        self.assertTrue(check_password('NewPassword2!', self.user.password))
    
    def test_post_invalid_form_shows_errors(self):
        """Prueba que muestra errores si el formulario es inválido."""
        response = self.client.post(self.url, {
            'contrasenia_actual': 'OldPassword1!',
            'contrasenia_nueva': 'short',
            'confirmacion_contrasenia': 'short'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
    
    def test_post_wrong_current_password(self):
        """Prueba que muestra un error si la contraseña actual es incorrecta."""
        response = self.client.post(self.url, {
            'contrasenia_actual': 'WrongPassword!',
            'contrasenia_nueva': 'NewPassword2!',
            'confirmacion_contrasenia': 'NewPassword2!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('contrasenia_actual', response.context['form'].errors)
        self.assertEqual(response.context['form'].errors['contrasenia_actual'][0], 'Contraseña incorrecta')
    
    def test_post_new_password_same_as_current(self):
        """Prueba que muestra un error si la nueva contraseña es igual a la actual."""
        response = self.client.post(self.url, {
            'contrasenia_actual': 'OldPassword1!',
            'contrasenia_nueva': 'OldPassword1!',
            'confirmacion_contrasenia': 'OldPassword1!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('contrasenia_nueva', response.context['form'].errors)
        self.assertEqual(response.context['form'].errors['contrasenia_nueva'][0], 'La contraseña nueva no puede ser igual a la anterior')
