from core.models import Reparacion

def get_all_reparaciones():
    return Reparacion.objects.all()

def crear_reparacion(form):
    return form.save()
