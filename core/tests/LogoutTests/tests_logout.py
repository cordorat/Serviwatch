from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from core.views.Logout.logout_view import logout_view
from django.http import HttpRequest
from django.contrib.sessions.middleware import SessionMiddleware
from unittest.mock import patch, MagicMock
from core.services.logout_service import cerrar_sesion

class LogoutViewTest(TestCase):
    @patch('core.views.Logout.logout_view.cerrar_sesion')
    def test_logout_view_calls_cerrar_sesion(self, mock_cerrar_sesion):
        # Arrange
        request = HttpRequest()
        
        # Act
        response = logout_view(request)
        
        # Assert
        mock_cerrar_sesion.assert_called_once_with(request)
        self.assertEqual(response.url, reverse('login'))

    def test_logout_view_redirects_to_login(self):
        # Act
        response = self.client.get('/logout/')
        
        # Assert
        self.assertRedirects(response, reverse('login'), fetch_redirect_response=False)


class LogoutServiceTest(TestCase):
    def setUp(self):
        self.request = HttpRequest()
        middleware = SessionMiddleware(get_response=lambda x: None)
        middleware.process_request(self.request)
        self.request.session.save()

    @patch('core.services.logout_service.logout')  # Changed patch path to match import location
    def test_cerrar_sesion_calls_logout(self, mock_logout):
        # Arrange
        self.request.session['some_key'] = 'some_value'
        
        # Act
        cerrar_sesion(self.request)
        
        # Assert
        mock_logout.assert_called_once_with(self.request)
        self.assertEqual(dict(self.request.session), {})
        self.assertFalse(self.request.session.items())