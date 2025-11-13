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
    estado = models.CharField(max_length=8, choices=(('activo','activo'),('inactivo','inactivo')), default='activo')
    
    # Cambiar CharField a ImageField para manejar imágenes de productos
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    # Fecha de vencimiento para inventario 
    fecha_vencimiento = models.DateField(null=True, blank=True)
    
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


# Señal: crear notificación cuando se agregue entrada de inventario
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Inventario)
def crear_notificacion_inventario(sender, instance, created, **kwargs):
    try:
        if created and instance.tipo_movimiento == 'Entrada':
            # Crear notificación para el producto asociado
            Notification.objects.create(producto=instance.producto)
    except Exception:
        # No interrumpir la transacción por fallos en notificaciones
        pass


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


class Promotion(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
    )

    TIPO_CHOICES = (
        ('2x1', '2x1'),
        ('descuento', 'Descuento'),
        ('oferta', 'Oferta especial'),
    )

    # Use db_constraint=False because `Producto` maps to a legacy table
    # whose primary key column attributes (e.g. unsigned) may not match
    # Django's default FK creation on MySQL. Avoid DB-level FK to prevent
    # incompatibility errors while keeping the relation at the ORM level.
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_constraint=False)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, db_constraint=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='descuento')
    discount_percent = models.IntegerField(null=True, blank=True)
    recommended_reason = models.TextField(blank=True, null=True)
    promotion_start = models.DateField(null=True, blank=True)
    promotion_end = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Promo {self.producto.nombre} - {self.get_tipo_display()} ({self.get_status_display()})"

    class Meta:
        ordering = ('-creado_en',)


# Modelo que mapea a la tabla externa `promociones` (managed=False porque ya existe en la DB)
class Promocion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    descuento = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    activo = models.CharField(max_length=2, choices=(('si','si'),('no','no')), default='si')

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'promociones'
        managed = False


# Crear notificación automáticamente al crear un producto
# Note: signal to auto-create Notification on Producto creation was removed to revert
# to the previous UX (notifications are shown from the `ultimos` endpoint).

# Señales para Producto: crear notificación al crear producto o al aumentar stock
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


@receiver(pre_save, sender=Producto)
def producto_pre_save(sender, instance, **kwargs):
    # Guardar el stock actual previo en un atributo temporal para su comparación en post_save
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            instance._previous_stock = old.stock_actual
        except sender.DoesNotExist:
            instance._previous_stock = None
    else:
        instance._previous_stock = None


@receiver(post_save, sender=Producto)
def producto_post_save(sender, instance, created, **kwargs):
    try:
        # Si es un producto nuevo, crear notificación
        if created:
            Notification.objects.create(producto=instance)
            return

        # Si no es nuevo, comprobar si el stock aumentó
        prev = getattr(instance, '_previous_stock', None)
        if prev is not None and instance.stock_actual > prev:
            Notification.objects.create(producto=instance)
    except Exception:
        # No bloquear la operación principal por fallos en notificaciones
        pass

class Empleado(models.Model):
    nombre = models.CharField(max_length=45, verbose_name="Nombre")
    email = models.EmailField(unique=True, verbose_name="Correo Electrónico")
    telefono = models.CharField(max_length=15, verbose_name="Teléfono")
    direccion = models.TextField(max_length=200, verbose_name="Dirección")

    def __str__(self):
        return self.nombre
