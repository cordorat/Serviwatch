from core.models.reloj import Reloj

def get_all_relojes():
    return Reloj.objects.all()

def create_reloj(form):
    reloj = form.save(commit=False)
    precio = form.cleaned_data.get('precio', '0')
    tiene_comision = form.cleaned_data.get('tiene_comision', False)

    try:
        comision = int(precio) * 0.2 if tiene_comision else 0
    except Exception as e:
        comision = 0
    reloj.comision = str(int(comision))
    
    reloj.save()
    return reloj