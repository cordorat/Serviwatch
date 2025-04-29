from django.urls import path
from core.views.login.login import Login
from core.views.login.recuperar_contraseña import recuperar_contraseña, cambiar_contraseña

urlpatterns = [
    path('', Login, name='login'),
    path('recuperarContraseña/', recuperar_contraseña, name='recuperar_contraseña'),
    path('cambiarContraseña/<str:token>/', cambiar_contraseña, name='cambiar_contraseña'),

]