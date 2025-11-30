#!/usr/bin/env python
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

with connection.cursor() as cursor:
    print("=" * 70)
    print("FOREIGN KEYS QUE REFERENCIAN usuarios.id")
    print("=" * 70)
    
    cursor.execute("""
        SELECT CONSTRAINT_NAME, TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE REFERENCED_TABLE_NAME = 'usuarios' 
        AND REFERENCED_COLUMN_NAME = 'id'
    """)
    
    for row in cursor.fetchall():
        print(f"\n  Constraint: {row[0]}")
        print(f"    Tabla origen: {row[1]}")
        print(f"    Columna origen: {row[2]}")
        print(f"    Tabla referenciada: {row[3]}")
