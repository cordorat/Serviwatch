from core.models.reloj import Reloj

def get_all_relojes():
    return Reloj.objects.all()

def create_reloj(form_data):
    return form_data.save()