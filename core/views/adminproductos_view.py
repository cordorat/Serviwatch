from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def admin_productos_view(request):
    return render(request, 'admin-productos.html')

@login_required
def admin_inventario_view(request):
    return render(request, 'usuario-productos.html')

