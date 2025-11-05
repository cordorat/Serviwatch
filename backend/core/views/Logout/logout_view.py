from django.shortcuts import redirect
from core.services.logout_service import cerrar_sesion
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

@login_required
@require_http_methods(["POST"])
def logout_view(request):
    cerrar_sesion(request)
    return redirect('login')