from core.models.reloj import Reloj

def get_all_relojes():
    return Reloj.objects.all()

def create_reloj(form):
    reloj = form.save(commit=False)
    precio = form.cleaned_data.get('precio', '0')
    try:
        comision = int(precio) * 0.2
    except Exception as e:
        print(f"Error calculando comisión: {e}")
        comision = 0
    reloj.comision = str(int(comision))
    if not reloj.estado:
        reloj.estado = 'DISPONIBLE'
    print(f"Guardando reloj con: precio={precio}, comision={reloj.comision}, estado={reloj.estado}")
    reloj.save()
    print(f"Reloj guardado con ID: {reloj.id}")
    return reloj