from django.urls import path
from core.views.login.login_view import login_view
from core.views.login.recuperar_contraseña import recuperar_contraseña, cambiar_contraseña

urlpatterns = [
    path('', login_view, name='login'),
    path('recuperarContraseña/', recuperar_contraseña, name='recuperar_contraseña'),
    path('cambiarContraseña/<str:token>/', cambiar_contraseña, name='cambiar_contraseña'),
]

