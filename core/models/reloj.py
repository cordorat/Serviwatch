from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator

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
        validators=[
            MaxLengthValidator(30, "Nombre de marca demasiado largo")
        ]
    )
    
    referencia = models.CharField(
        max_length=30,
        validators=[
            MaxLengthValidator(30, "Referencia demasiado larga")
        ]
    )

    precio = models.CharField(
        max_length=20,
        validators=[
            MinLengthValidator(1, message="El precio debe ser mayor a 0."),
            MaxLengthValidator(20, "Precio demasiado grande"),
            RegexValidator(
                regex=r'^\d+(\.\d{1,2})?$',
                message="El precio debe ser un número válido con hasta dos decimales."
            ),
        ]
    )

    comision = models.CharField(
        max_length=20,
        editable=False,
        validators=[
            MaxLengthValidator(20, "Comisión demasiado grande"),
            RegexValidator(
                regex=r'^\d+(\.\d{1,2})?$',
                message="La comisión debe ser un número válido con hasta dos decimales."
            ),
        ]
    )

    dueño = models.CharField(
        max_length=50,
        validators=[
            MaxLengthValidator(50, "Nombre del dueño demasiado largo")
        ]
    )
    
    descripcion = models.TextField(
        max_length=150,
        validators=[
            MaxLengthValidator(150, "Descripción demasiado larga")
        ]
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

    def clean(self):
        if self.estado == 'VENDIDO' and not self.fecha_venta:
            raise ValidationError("Debe ingresar la fecha de venta si el reloj fue vendido.")

        # Validar que el precio sea numérico y positivo
        try:
            precio_float = float(self.precio)
            if precio_float <= 0:
                raise ValidationError("El precio debe ser un valor positivo mayor que cero.")
        except ValueError:
            raise ValidationError("El precio debe ser un número válido.")

        # Validar que comision sea correcta
        expected_comision = round(precio_float * 0.2, 2)
        try:
            comision_float = float(self.comision)
        except ValueError:
            raise ValidationError("La comisión guardada no es un número válido.")
        if round(comision_float, 2) != expected_comision:
            raise ValidationError(f"La comisión debe ser el 20% del precio. Comisión calculada: {expected_comision}.")

        # Validar longitud
        if len(self.precio) > 20:
            raise ValidationError("Precio demasiado largo.")
        if len(self.comision) > 20:
            raise ValidationError("Comisión demasiado larga.")

    def save(self, *args, **kwargs):
        try:
            precio_float = float(self.precio)
            self.comision = str(round(precio_float * 0.2, 2))
        except ValueError:
            self.comision = '0.00'  # fallback en caso de error
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.marca} - {self.referencia} - ${self.precio} - {self.get_tipo_display()}"
