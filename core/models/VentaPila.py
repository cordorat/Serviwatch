from django.db import models
from core.models.pilas import Pilas
from core.models.ingreso import Ingreso
from datetime import date

class VentaPila(models.Model):
    pila = models.ForeignKey(Pilas, on_delete=models.CASCADE, related_name='ventas')
    cantidad = models.PositiveIntegerField()
    fecha_venta = models.DateTimeField(auto_now_add=True)
    valor_total = models.PositiveIntegerField(default=0)
    
    def _str_(self):
        return f"Venta {self.id} - {self.pila.codigo} - {self.cantidad} unidades"
    
    def calcular_valor_total(self):
        if self.pila and self.cantidad:
            try:
                return int(self.pila.precio) * self.cantidad
            except (ValueError, TypeError):
                return 0
        return 0
    
    def save(self, *args, **kwargs):
        """sobreescribir el método save para calcular el valor total antes de guardar"""
        self.valor_total = self.calcular_valor_total()
        
        # Guardar primero la venta para obtener el ID
        super().save(*args, **kwargs)
        
        # Crear un ingreso asociado a esta venta
        Ingreso.objects.create(
            fecha=date.today(),  # Convertir DateTime a Date ya que Ingreso usa DateField
            valor=self.valor_total,
            descripcion=f"Venta pilas {self.pila.codigo}, x {self.cantidad} unidades"
        )