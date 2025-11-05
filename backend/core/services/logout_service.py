from django.contrib.auth import logout

def cerrar_sesion(request):
    logout(request)
    request.session.flush()
    return None