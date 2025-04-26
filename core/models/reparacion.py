from django.db import models
from django.contrib.auth.models import User
from core.models import Cliente 

class Reparacion(models.Model):
    ESTADOS = [
        ('cotización', 'Cotización'),
        ('reparación', 'En reparación'),
        ('prueba', 'En prueba'),
        ('entregado', 'Entregado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    marca_reloj = models.CharField(max_length=30)
    descripcion = models.TextField(max_length=500)
    codigo_orden = models.CharField(max_length=10, unique=True)
    fecha_ingreso = models.DateField(auto_now_add=True)
    fecha_entrega_estimada = models.DateField()
    precio = models.PositiveIntegerField()
    espacio_fisico = models.CharField(max_length=15)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='cotización')
    tecnico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'is_staff': True})

    def __str__(self):
        return f"Reparación {self.codigo_orden} - {self.cliente}"

