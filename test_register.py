#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from usuarios.models import Usuario, Rol
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

print("=" * 70)
print("TEST: CREAR NUEVO USUARIO")
print("=" * 70)

# Datos de prueba
email = f"test_cliente_{int(__import__('time').time())}@test.com"
nombre = "Cliente Test"
password = "TestPassword123!"

try:
    print(f"\n1. Creando Usuario personalizado...")
    
    rol_cliente, _ = Rol.objects.get_or_create(nombre='Cliente')
    print(f"   Rol encontrado/creado: {rol_cliente.nombre}")
    
    usuario = Usuario.objects.create(
        nombre=nombre,
        email=email,
        password=make_password(password),
        rol=rol_cliente,
        estado='activo'
    )
    print(f"   ✅ Usuario creado: ID={usuario.id}, Email={usuario.email}")
    
    print(f"\n2. Creando User en auth_user...")
    user_auth = User.objects.create_user(
        username=email,
        email=email,
        password=password
    )
    user_auth.is_active = True
    user_auth.save()
    print(f"   ✅ Auth User creado: ID={user_auth.id}, Username={user_auth.username}")
    
    print(f"\n✅ ÉXITO: Nuevo usuario registrado correctamente")
    print(f"   Email: {email}")
    print(f"   Nombre: {nombre}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
