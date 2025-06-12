from core.models.reloj import Reloj

def get_all_relojes():
    return Reloj.objects.all()

def create_reloj(form):
    reloj = form.save(commit=False)
    precio = form.cleaned_data.get('precio')
    tiene_comision = form.cleaned_data.get('tiene_comision')

    try:
        comision = int(precio) * 0.2 if tiene_comision else 0
    except Exception as e:
        comision = 0
    reloj.comision = str(int(comision))

    reloj.saldo_pendiente = str(precio)
    reloj.pagado = False

    reloj.save()
    return reloj