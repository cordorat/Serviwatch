"""
URL configuration for Serviwatch project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core.urls import urlpatterns as core_urls
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # Admin de Django
    path('admin/', admin.site.urls),
    
    # URLs tradicionales del proyecto (templates HTML)
    path('', include(core_urls)),
    
    # ============================================
    # API REST - Endpoints JSON
    # ============================================
    
    # Autenticación JWT
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API de la aplicación
    path('api/', include('core.urls.api_urls')),
    
    # Navegador de API de DRF (útil para desarrollo)
    path('api-auth/', include('rest_framework.urls')),
]
