from core.models import Cliente

def get_all_clientes():
    return Cliente.objects.all()