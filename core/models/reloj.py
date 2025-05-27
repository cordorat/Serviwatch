from django.db import models
from django.core.validators import MaxLengthValidator, RegexValidator
from core.models.cliente import Cliente


class Reloj(models.Model):

    TIPO_CHOICES = [
        ('NUEVO', 'Nuevo'),
        ('USADO', 'Usado'),
        ('SEMI', 'Seminuevo'),
    ]

    ESTADO_CHOICES = [
        ('VENDIDO', 'Vendido'),
        ('DISPONIBLE', 'Disponible'),
    ]

    marca = models.CharField(
        max_length=30,
        validators=[MaxLengthValidator(30, "Nombre de marca demasiado largo")]
    )
    
    referencia = models.CharField(
        max_length=30,
        validators=[MaxLengthValidator(30, "Referencia demasiado larga")]
    )

    precio = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(regex=r'^\d+$', message="El precio debe ser un número válido"),
            MaxLengthValidator(20, "El precio no puede exceder los 20 caracteres")],
    )

    comision = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(regex=r'^\d+$', message="La comision debe ser un número válido"),
            MaxLengthValidator(20, "La comision no puede exceder los 20 caracteres"),
        ]
    )

    dueno = models.CharField(
        max_length=50,
        validators=[MaxLengthValidator(50, "Nombre del dueño demasiado largo")]
    )
    
    descripcion = models.TextField(
        max_length=150,
        validators=[MaxLengthValidator(150, "Descripción demasiado larga")]
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='DISPONIBLE'
    )

    fecha_venta = models.DateField(
        blank=True,
        null=True
    )

    pagado = models.BooleanField(default=False)

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.marca} - {self.referencia} - ${self.precio} - {self.get_tipo_display()}"
