from django.db import models

class Empleado(models.Model):
    CARGO_CHOICES = (
        ('Técnico', 'Técnico'),
        ('Secretario/a', 'Secretario/a'),
    )

    ESTADO_CHOICES = (
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
    )

    cedula = models.BigIntegerField(unique=True)
    nombre = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    fecha_ingreso = models.DateField()
    fecha_nacimiento = models.DateField()
    celular = models.BigIntegerField()
    cargo = models.CharField(max_length=20, choices=CARGO_CHOICES)
    salario = models.BigIntegerField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='Activo')

    def __str__(self):
        return f"{self.nombre} {self.apellidos} - {self.cedula}"
