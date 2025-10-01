from django.db import models

# Roles
class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# Usuarios
class Usuario(models.Model):
    ROLES_CHOICES = (
        ('Administrador', 'Administrador'),
        ('Empleado', 'Empleado'),
        ('Cliente', 'Cliente'),
    )
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=10, choices=(('activo','activo'),('inactivo','inactivo')), default='activo')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre
