from django.urls import include, path

urlpatterns = [
    path('', include('core.urls.cliente_urls')),
    path('', include('core.urls.reparacion_urls')),
]