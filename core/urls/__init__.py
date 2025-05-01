from django.urls import include, path

urlpatterns = [
    path('', include('core.urls.cliente_urls')),
    path('', include('core.urls.login_urls')),
    path('', include('core.urls.reparacion_urls')),
    path('', include('core.urls.empleado_urls')),
    path('', include('core.urls.usuario_urls')),
    path('', include('core.urls.logout_urls')),]
