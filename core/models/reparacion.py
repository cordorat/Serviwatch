from django.db import models
from core.models.cliente import Cliente 
from core.models.empleado import Empleado

class Reparacion(models.Model):
    ESTADOS = [
        ('Cotización', 'Cotización'),
        ('Reparación', 'En reparación'),
        ('Prueba', 'En prueba'),
        ('Listo', 'Listo para entrega'),
        ('Entregado', 'Entregado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    marca_reloj = models.CharField(max_length=30)
    descripcion = models.TextField(max_length=500)
    codigo_orden = models.CharField(max_length=10, unique=True)
    fecha_ingreso = models.DateField(auto_now_add=True)
    fecha_entrega_estimada = models.DateField()
    precio = models.PositiveIntegerField()
    espacio_fisico = models.CharField(max_length=15)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='Cotización')
    tecnico = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, related_name='reparaciones')

    def __str__(self):
        return f"Reparación {self.codigo_orden} - {self.cliente}"

