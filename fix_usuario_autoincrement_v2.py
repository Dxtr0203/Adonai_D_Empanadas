#!/usr/bin/env python
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

with connection.cursor() as cursor:
    print("=" * 70)
    print("PROCESO: AGREGAR AUTO_INCREMENT A usuarios.id")
    print("=" * 70)
    
    # 1. Eliminar FK
    print("\n1. Eliminando FK temporalmente...")
    try:
        cursor.execute("""
            ALTER TABLE ventas_venta 
            DROP FOREIGN KEY ventas_venta_usuario_id_a710a973_fk_usuarios_id
        """)
        print("   ✅ FK eliminado")
    except Exception as e:
        print(f"   ⚠️ {e}")
    
    # 2. Modificar usuarios.id
    print("\n2. Modificando usuarios.id a AUTO_INCREMENT...")
    try:
        cursor.execute("""
            ALTER TABLE usuarios 
            MODIFY COLUMN id BIGINT AUTO_INCREMENT
        """)
        print("   ✅ AUTO_INCREMENT agregado")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Recrear FK
    print("\n3. Recreando FK...")
    try:
        cursor.execute("""
            ALTER TABLE ventas_venta 
            ADD CONSTRAINT ventas_venta_usuario_id_fk_usuarios
            FOREIGN KEY (usuario_id) 
            REFERENCES usuarios (id)
        """)
        print("   ✅ FK recreado")
    except Exception as e:
        print(f"   ⚠️ {e}")
    
    # 4. Verificar
    print("\n4. Verificando estructura...")
    cursor.execute("DESCRIBE usuarios")
    for row in cursor.fetchall():
        if row[0] == 'id':
            print(f"   {row[0]:20} {row[1]:20} {row[5]:30}")
