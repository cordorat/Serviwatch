from django.urls import path
from core.views.login.login_view import login_view
from core.views.usuarioservicios_view import usuario_servicios_view
from core.views.usuarioproductos_view import usuario_productos_view
from core.views.login.recuperar_contraseña import recuperar_contrasenia, cambiar_contrasenia
from core.views.usuario_contabilidad_view import usuario_contabilidad_view

urlpatterns = [
    path('', login_view, name='login'),
    path('recuperarContraseña/', recuperar_contrasenia, name='recuperar_contraseña'),
    path('cambiarContraseña/<str:token>/', cambiar_contrasenia, name='cambiar_contraseña'),
    path('servicios/', usuario_servicios_view, name='servicios_usuario'),
    path('productos/', usuario_productos_view, name='productos_usuario'),
    path('', login_view, name='login'),
    path('recuperarContraseña/', recuperar_contrasenia, name='recuperar_contraseña'),
    path('cambiarContraseña/<str:token>/', cambiar_contrasenia, name='cambiar_contraseña'),
    path('contable/', usuario_contabilidad_view, name='contabilidad_usuario'),
]
