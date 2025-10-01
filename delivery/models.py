from django.db import models
from ventas.models import Venta
from usuarios.models import Usuario

class Delivery(models.Model):
    ESTADO_CHOICES = (
        ('pendiente','pendiente'),
        ('en camino','en camino'),
        ('entregado','entregado'),
        ('cancelado','cancelado')
    )
    venta = models.OneToOneField(Venta, on_delete=models.CASCADE)
    direccion_completa = models.TextField()
    ciudad = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20)
    repartidor = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='entregas')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_entrega_estimada = models.DateTimeField(blank=True, null=True)
    fecha_entrega_real = models.DateTimeField(blank=True, null=True)
