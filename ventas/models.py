from django.db import models
from usuarios.models import Usuario
from productos.models import Producto

class Venta(models.Model):
    ESTADO_CHOICES = (
        ('pendiente','pendiente'),
        ('pagado','pagado'),
        ('en_preparacion','en_preparacion'),
        ('en_envio','en_envio'),
        ('entregado','entregado'),
        ('cancelado','cancelado')
    )
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    metodo_pago = models.CharField(max_length=20, choices=(('Efectivo','Efectivo'),('Tarjeta','Tarjeta'),('Transferencia','Transferencia'),('Otro','Otro')))
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    direccion_entrega = models.TextField(blank=True, null=True)
    ciudad_entrega = models.CharField(max_length=100, blank=True, null=True)
    codigo_postal = models.CharField(max_length=20, blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

class VentaDetalle(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
