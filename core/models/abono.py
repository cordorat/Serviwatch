from django.db import models
from django.core.validators import MaxLengthValidator, RegexValidator

class Abono(models.Model):
    reloj = models.ForeignKey(
        'Reloj',
        on_delete=models.CASCADE,
        related_name='abonos'
    )
    monto = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message="El monto debe ser un número válido"
            ),
            MaxLengthValidator(
                20,
                "El monto no puede exceder los 20 caracteres"
            )
        ],
        verbose_name="Monto del abono"
    )
    fecha = models.DateField(
        auto_now_add=True,
        verbose_name="Fecha del abono"
    )
    descripcion = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Descripción"
    )

    class Meta:
        ordering = ['-fecha']
        verbose_name = "Abono"
        verbose_name_plural = "Abonos"

    def __str__(self):
        return f"Abono de ${self.monto} para {self.reloj}"
