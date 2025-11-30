#!/usr/bin/env python
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

with connection.cursor() as cursor:
    print("=" * 70)
    print("TIPOS DE DATO en tablas")
    print("=" * 70)
    
    tables = ['productos', 'productos_producto', 'ventas_ventadetalle']
    
    for tabla in tables:
        print(f"\n{tabla}:")
        cursor.execute(f"DESCRIBE {tabla}")
        for row in cursor.fetchall():
            if row[0] in ['id', 'producto_id']:
                print(f"  {row[0]:20} {row[1]}")
