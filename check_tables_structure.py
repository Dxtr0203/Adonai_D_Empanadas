#!/usr/bin/env python
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

with connection.cursor() as cursor:
    print("=" * 70)
    print("ESTRUCTURA TABLA venta_detalles")
    print("=" * 70)
    cursor.execute("DESCRIBE venta_detalles")
    for row in cursor.fetchall():
        print(row)
    
    print("\n" + "=" * 70)
    print("CONTENIDO venta_detalles (primeros 5)")
    print("=" * 70)
    cursor.execute("SELECT * FROM venta_detalles LIMIT 5")
    for row in cursor.fetchall():
        print(row)
    
    print("\n" + "=" * 70)
    print("CONSTRAINTS venta_detalles")
    print("=" * 70)
    cursor.execute("""
        SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_NAME = 'venta_detalles'
    """)
    for row in cursor.fetchall():
        print(row)
    
    print("\n" + "=" * 70)
    print("TABLA ventas (primeros 5 IDs)")
    print("=" * 70)
    cursor.execute("SELECT id, usuario_id, total, creado_en FROM ventas LIMIT 5")
    for row in cursor.fetchall():
        print(row)
