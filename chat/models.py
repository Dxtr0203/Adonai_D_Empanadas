from django.db import models
from usuarios.models import Usuario

class Chat(models.Model):
    ESTADO_CHOICES = (
        ('esperando','esperando'),
        ('en_atencion','en_atencion'),
        ('finalizado','finalizado'),
        ('cancelado','cancelado')
    )
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='esperando')
    prioridad = models.IntegerField(default=0)
    llegada = models.DateTimeField(auto_now_add=True)
    inicio_servicio = models.DateTimeField(blank=True, null=True)
    fin_servicio = models.DateTimeField(blank=True, null=True)
    duracion_segundos = models.IntegerField(blank=True, null=True)

class MensajeChat(models.Model):
    REMITENTE_CHOICES = (
        ('Usuario','Usuario'),
        ('Bot','Bot'),
        ('Empleado','Empleado')
    )
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    remitente = models.CharField(max_length=20, choices=REMITENTE_CHOICES)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
