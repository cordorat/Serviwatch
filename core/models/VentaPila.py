from django.db import models
from core.models.pilas import Pilas

class VentaPila(models.Model):
    pila = models.ForeignKey(Pilas, on_delete=models.CASCADE, related_name='ventas')
    cantidad = models.PositiveIntegerField()
    fecha_venta = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Venta {self.id} - {self.pila.codigo} - {self.cantidad} unidades"