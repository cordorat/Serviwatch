from core.models.empleado import Empleado

def crear_empleado(form):
    empleado = form.save()
    return empleado

def get_all_empleados(filtro_estado=None, busqueda_cedula=None):
    empleados = Empleado.objects.all()

    if filtro_estado:
        empleados = empleados.filter(estado=filtro_estado)

    if busqueda_cedula:
        empleados = empleados.filter(cedula__icontains=busqueda_cedula)

    return empleados.order_by('nombre')
