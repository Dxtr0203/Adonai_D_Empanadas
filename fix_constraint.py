#!/usr/bin/env python
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

print("=" * 70)
print("CORRIGIENDO CONSTRAINT de ventas_ventadetalle")
print("=" * 70)

with connection.cursor() as cursor:
    # Primero, eliminar el constraint incorrecto
    print("\n1. Eliminando constraint incorrecto...")
    try:
        cursor.execute("""
            ALTER TABLE ventas_ventadetalle 
            DROP FOREIGN KEY ventas_ventadetalle_producto_id_30eb3c7e_fk_productos
        """)
        print("   ✅ Constraint eliminado")
    except Exception as e:
        print(f"   ⚠️ {e}")
    
    # Crear el constraint correcto
    print("\n2. Creando constraint correcto...")
    try:
        cursor.execute("""
            ALTER TABLE ventas_ventadetalle 
            ADD CONSTRAINT ventas_ventadetalle_producto_id_fk_productos
            FOREIGN KEY (producto_id) 
            REFERENCES productos (id)
        """)
        print("   ✅ Constraint creado")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Verificar constraints finales
    print("\n3. Verificando constraints...")
    cursor.execute("""
        SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_NAME = 'ventas_ventadetalle'
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]:50} | {row[1]:15} -> {row[2]}")
