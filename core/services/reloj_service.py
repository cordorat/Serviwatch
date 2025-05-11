from core.models.reloj import Reloj

def get_all_relojes():
    return Reloj.objects.all()

def create_reloj(form):
    reloj = form.save(commit=False)  # Guardamos el objeto pero no lo confirmamos aún
    precio = form.cleaned_data.get('precio', '0')  # Obtenemos el precio como string
    comision = int(precio) * 0.2  # Calculamos la comisión
    reloj.comision = str(int(comision))  # Asignamos la comisión como string
    reloj.save()  # Ahora sí lo guardamos en la base de datos
    return reloj