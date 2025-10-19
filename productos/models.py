from django.db import models
from usuarios.models import Usuario

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'categorias'
        # managed=False para indicar que la tabla ya existe en la base legacy
        managed = False

class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock_minimo = models.IntegerField(default=0)
    stock_actual = models.IntegerField(default=0)
    estado = models.CharField(max_length=10, choices=(('activo','activo'),('inactivo','inactivo')), default='activo')
    
    # Cambiar CharField a ImageField para manejar imágenes de productos
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos_creados', db_column='creado_por')
    actualizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos_actualizados', db_column='actualizado_por')
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'productos'
        managed = False

class Inventario(models.Model):
    TIPO_MOVIMIENTO = (
        ('Entrada','Entrada'),
        ('Salida','Salida'),
        ('Ajuste','Ajuste')
    )
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    tipo_movimiento = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO)
    observacion = models.CharField(max_length=255, blank=True, null=True)
    referencia = models.CharField(max_length=100, blank=True, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_movimiento = models.DateTimeField(auto_now_add=True)


# Notificaciones por producto nuevo
class Notification(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notif: {self.producto.nombre} - {self.creado_en}"


class NotificationRead(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='reads')
    # usamos auth.User para llevar el estado por usuario
    from django.contrib.auth.models import User
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('notification', 'user')


# Crear notificación automáticamente al crear un producto
# Note: signal to auto-create Notification on Producto creation was removed to revert
# to the previous UX (notifications are shown from the `ultimos` endpoint).
