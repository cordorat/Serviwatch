from django.db import models
from core.models.pilas import Pilas


class VentaPila(models.Model):
    pila = models.ForeignKey(
        Pilas, on_delete=models.CASCADE, related_name='ventas')
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.PositiveIntegerField(default=0)
    fecha_venta = models.DateTimeField(auto_now_add=True)

    @property
    def precio_total(self):
        """Calcula el precio total de esta venta"""
        return self.precio_unitario * self.cantidad

    def __str__(self):
        return f"Venta {self.id} - {self.pila.codigo} - {self.cantidad} unidades"
