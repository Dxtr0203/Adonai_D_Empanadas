# Script para crear usuario de prueba si hace falta y ejecutar chat_personalizado
from django.test import RequestFactory
from chat.views import chat_personalizado
from usuarios.models import Usuario, Rol
import json

# Asegurar rol y usuario
rol, _ = Rol.objects.get_or_create(nombre='Cliente', defaults={'descripcion': 'Rol por defecto'})
user, created = Usuario.objects.get_or_create(
    email='prueba@example.com',
    defaults={'nombre': 'Prueba', 'password': 'x', 'rol': rol}
)
print('Usuario id:', user.id, ' (created)' if created else ' (existing)')

# Crear request simulado
factory = RequestFactory()
request = factory.post(
    '/chat/personalizado/',
    data=json.dumps({'usuario_id': user.id, 'message': 'Test urgente desde script'}),
    content_type='application/json'
)

# Ejecutar vista
response = chat_personalizado(request)
print('RESPUESTA:')
try:
    print(response.content.decode())
except Exception:
    print(response)
