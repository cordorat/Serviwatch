from django.db import models
from django.core.validators import RegexValidator


class Empleado(models.Model):
    CARGO_CHOICES = (
        ('Técnico', 'Técnico'),
        ('Secretario/a', 'Secretario/a'),
    )

    ESTADO_CHOICES = (
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
    )

    cedula = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{1,10}$',
                message='La cédula debe contener solo números y tener máximo 10 dígitos.'
            )
        ]   
    )
    nombre = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    fecha_ingreso = models.DateField()
    fecha_nacimiento = models.DateField()
    celular = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^3\d{9}$',
                message='El número de celular debe comenzar con 3 y tener 10 dígitos en total.'
            )
        ]
    )
    cargo = models.CharField(max_length=20, choices=CARGO_CHOICES)
    salario = models.CharField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='Activo')

    def __str__(self):
        return f"{self.nombre} {self.apellidos} - {self.cedula}"
