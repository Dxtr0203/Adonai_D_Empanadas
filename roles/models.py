# roles/models.py
from django.db import models

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre
