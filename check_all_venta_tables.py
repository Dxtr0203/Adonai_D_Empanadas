#!/usr/bin/env python
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

with connection.cursor() as cursor:
    print("=" * 70)
    print("LISTAR TODAS LAS TABLAS RELACIONADAS CON VENTA")
    print("=" * 70)
    cursor.execute("""
        SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = 'adonai_store' 
        AND TABLE_NAME LIKE '%venta%'
        ORDER BY TABLE_NAME
    """)
    for row in cursor.fetchall():
        print(f"  - {row[0]}")
    
    print("\n" + "=" * 70)
    print("CONTENIDO DE CADA TABLA")
    print("=" * 70)
    
    cursor.execute("SELECT COUNT(*) FROM ventas")
    print(f"ventas: {cursor.fetchone()[0]} registros")
    
    cursor.execute("""
        SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = 'adonai_store' 
        AND TABLE_NAME LIKE '%venta%'
        AND TABLE_NAME != 'ventas'
    """)
    
    for table in cursor.fetchall():
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"{table_name}: {count} registros")
