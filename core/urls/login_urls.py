from django.urls import path
from core.views.login.login_view import login_view
from core.views.usuarioservicios_view import usuario_servicios_view
from core.views.usuarioproductos_view import usuario_productos_view
from core.views.login.recuperar_contraseña import recuperar_contraseña, cambiar_contraseña

urlpatterns = [
    path('', login_view, name='login'),
    path('recuperarContraseña/', recuperar_contraseña, name='recuperar_contraseña'),
    path('cambiarContraseña/<str:token>/', cambiar_contraseña, name='cambiar_contraseña'),
    path('servicios/', usuario_servicios_view, name='servicios_usuario'),
    path('productos/', usuario_productos_view, name='productos_usuario'),
    path('', login_view, name='login'),
    path('recuperarContraseña/', recuperar_contraseña, name='recuperar_contraseña'),
    path('cambiarContraseña/<str:token>/', cambiar_contraseña, name='cambiar_contraseña'),
]
