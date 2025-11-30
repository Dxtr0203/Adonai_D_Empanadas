#!/usr/bin/env python
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

print("=" * 70)
print("CORRIGIENDO TIPOS DE DATO Y CONSTRAINTS")
print("=" * 70)

with connection.cursor() as cursor:
    # Primero, cambiar el tipo de dato de producto_id
    print("\n1. Cambiando tipo de producto_id de BIGINT a INT...")
    try:
        cursor.execute("""
            ALTER TABLE ventas_ventadetalle 
            MODIFY COLUMN producto_id INT
        """)
        print("   ✅ Tipo de dato modificado")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Luego crear el constraint correcto
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
        print(f"   ⚠️ {e}")
    
    # Verificar
    print("\n3. Verificando constraints...")
    cursor.execute("""
        SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_NAME = 'ventas_ventadetalle'
    """)
    for row in cursor.fetchall():
        ref_table = row[2] if row[2] else "None"
        print(f"   {row[0]:50} | {row[1]:15} -> {ref_table}")
