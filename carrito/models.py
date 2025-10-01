from django.db import models
from usuarios.models import Usuario
from productos.models import Producto

class Carrito(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    creado_en = models.DateTimeField(auto_now_add=True)

class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField(default=1)
    agregado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('carrito','producto')
