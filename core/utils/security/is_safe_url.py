from django.conf import settings
from urllib.parse import urlparse
from django.urls import resolve, Resolver404

def is_safe_url(url):
    """
    Valida si una URL de redirección es segura
    """
    if not url:
        return False
    
    # Obtener el dominio de la URL
    url_info = urlparse(url)
    
    # Verificar si es una ruta relativa
    if not url_info.netloc:
        try:
            # Verificar si la ruta existe en las URLs de Django
            resolve(url_info.path)
            return True
        except Resolver404:
            return False
    
    # Si es una URL absoluta, verificar el dominio
    return url_info.netloc in settings.ALLOWED_HOSTS