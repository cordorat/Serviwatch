from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from django.db import models

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(regex=r'^\d+$', message='El teléfono debe contener solo números.'),
            MinLengthValidator(10, message='El teléfono debe tener 10  números.'),
            MaxLengthValidator(10, "El teléfono debe tener 10  números.")
        ]
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido}"