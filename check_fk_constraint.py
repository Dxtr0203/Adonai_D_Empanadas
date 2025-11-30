#!/usr/bin/env python
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

with connection.cursor() as cursor:
    print("=" * 70)
    print("CONSTRAINTS en ventas_ventadetalle")
    print("=" * 70)
    cursor.execute("""
        SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_NAME = 'ventas_ventadetalle'
    """)
    for row in cursor.fetchall():
        print(row)
    
    print("\n" + "=" * 70)
    print("TABLAS productos en la BD")
    print("=" * 70)
    cursor.execute("""
        SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = 'adonai_store' 
        AND TABLE_NAME LIKE '%producto%'
        ORDER BY TABLE_NAME
    """)
    for row in cursor.fetchall():
        tabla = row[0]
        cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
        count = cursor.fetchone()[0]
        print(f"  {tabla:30} ({count:3} registros)")
