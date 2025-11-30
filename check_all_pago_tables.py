#!/usr/bin/env python
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

with connection.cursor() as cursor:
    print("=" * 70)
    print("LISTAR TODAS LAS TABLAS RELACIONADAS CON PAGO")
    print("=" * 70)
    cursor.execute("""
        SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = 'adonai_store' 
        AND TABLE_NAME LIKE '%pago%'
        ORDER BY TABLE_NAME
    """)
    for row in cursor.fetchall():
        print(f"  - {row[0]}")
        
        cursor.execute(f"DESCRIBE {row[0]}")
        print("    Columnas:")
        for col in cursor.fetchall():
            print(f"      {col[0]:25} {col[1]}")
        print()
