from django.db import models

class Pilas (models.Model):
    codigo = models.CharField(max_length=30, unique=True)
    precio = models.CharField(max_length=6)
    cantidad = models.CharField(max_length=3)

    def __str__(self):
        return f"{self.codigo} - {self.precio} - {self.cantidad}"