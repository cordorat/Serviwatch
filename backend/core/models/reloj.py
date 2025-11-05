from django.db import models
from django.core.validators import MaxLengthValidator, RegexValidator
from core.models.cliente import Cliente

FORMATO_REGEX = r'^\d+$'

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

    METODO_PAGO_CHOICES = [
        ('CONTADO', 'Contado'),
        ('ABONO', 'Abono'),
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
            RegexValidator(regex=FORMATO_REGEX, message="El precio debe ser un número válido"),
            MaxLengthValidator(20, "El precio no puede exceder los 20 caracteres")],
    )

    tiene_comision = models.BooleanField(
        default=False,
        verbose_name="¿Tiene comisión?"
        )

    comision = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(regex=FORMATO_REGEX, message="La comision debe ser un número válido"),
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

    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_PAGO_CHOICES,
        default='ABONO'
    )

    saldo_pendiente = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(regex=FORMATO_REGEX, message="El saldo pendiente debe ser un número válido"),
            MaxLengthValidator(20, "El saldo pendiente no puede exceder los 20 caracteres")
        ]
    )

    def __str__(self):
        return f"{self.marca} - {self.referencia} - ${self.precio} - {self.get_tipo_display()}"
    
    def save(self, *args, **kwargs):
        # Si es nuevo o no tiene saldo_pendiente, inicializarlo con el precio
        if not self.pk or not self.saldo_pendiente:
            self.saldo_pendiente = str(self.precio) if self.precio else '0'
            print(f"Reloj {self.id}: Inicializando saldo_pendiente={self.saldo_pendiente}")
        
        # Si tiene_comision está marcado, calcular la comisión
        if self.tiene_comision and self.precio:
            try:
                precio = int(self.precio)
                self.comision = str(int(precio * 0.2))  # 20% del precio
            except (ValueError, TypeError):
                self.comision = '0'
        
        super().save(*args, **kwargs)
    