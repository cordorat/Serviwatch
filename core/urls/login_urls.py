from django.urls import path
from core.views.login.login_view import login_view
from core.views.usuarioservicios_view import usuario_servicios_view

urlpatterns = [
    path('', login_view, name='login'),
    path('servicios/', usuario_servicios_view, name='servicios_usuario')
]