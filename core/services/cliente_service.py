from core.models import Cliente

def get_all_clientes():
    return Cliente.objects.all()

def crear_cliente(form):
    return form.save()