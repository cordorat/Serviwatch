from django.db import models

class Ingreso(models.Model):
    fecha =models.DateField()
    valor = models.IntegerField()
    descripcion = models.TextField(max_length=100)
    
    def __str__(self):
        return f"Egreso: {self.valor} - {self.fecha} - {self.descripcion}"