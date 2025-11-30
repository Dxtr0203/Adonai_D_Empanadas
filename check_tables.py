#!/usr/bin/env python
"""
Ver el nombre exacto de las tablas
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from django.db import connection
from django.apps import apps

print("=" * 80)
print("TABLAS EN LA BD")
print("=" * 80)

with connection.cursor() as cursor:
    # Obtener todas las tablas
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    
    print("\nTablas relacionadas a productos:")
    for table in tables:
        table_name = table[0]
        if 'producto' in table_name.lower():
            print(f"  - {table_name}")
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"    → {count} registros")

print("\n" + "=" * 80)
