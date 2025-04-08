from django.contrib import admin
from core.models import Cliente

# Register your models here.
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellido', 'telefono')
    search_fields = ('nombre', 'apellido', 'telefono')