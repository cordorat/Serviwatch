from django.shortcuts import redirect
from core.services.logout_service import cerrar_sesion

def logout_view(request):
    cerrar_sesion(request)
    return redirect('login')