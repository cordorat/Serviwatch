from django.core.validators import  MaxLengthValidator, MaxValueValidator
from django.db import models
from django.core.exceptions import ValidationError
class Egreso(models.Model):
    valor = models.DecimalField(max_digits=10, decimal_places=0)
    fecha = models.DateField()
    descripcion = models.TextField(max_length=110)



   