import os
import django
import secrets

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from usuarios.models import Usuario, Rol
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.test import Client

email = 'empleado_test_script@example.com'
# cleanup
Usuario.objects.filter(email=email).delete()
base = 'empleado'

Rol.objects.get_or_create(nombre='Empleado', defaults={'descripcion': 'Empleado'})
rol = Rol.objects.get(nombre='Empleado')

raw_pw = secrets.token_urlsafe(8)
# generate unique username
username = base
i = 1
while User.objects.filter(username=username).exists():
    username = f"{base}{i}"
    i += 1

u = Usuario(nombre='Empleado Script', email=email, telefono='', direccion='', rol=rol, password=make_password(raw_pw), must_change_password=True)
u.save()

auth = User.objects.create(username=username, email=email)
auth.set_password(raw_pw)
auth.save()

print('CREATED', username, raw_pw)

client = Client()
resp = client.post('/usuarios/login/', {'username': username, 'password': raw_pw}, follow=True)
print('STATUS', resp.status_code)
print('REDIRECT_CHAIN', resp.redirect_chain)
print('FINAL_PATH', resp.request.get('PATH_INFO'))
