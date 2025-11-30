#!/usr/bin/env python
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

with connection.cursor() as cursor:
    print("=" * 70)
    print("VENTAS CON IDs 1741-1745")
    print("=" * 70)
    cursor.execute("SELECT id, usuario_id, total, creado_en FROM ventas WHERE id BETWEEN 1741 AND 1745")
    results = cursor.fetchall()
    print(f"Total encontradas: {len(results)}\n")
    for row in results:
        print(row)
    
    print("\n" + "=" * 70)
    print("RANGO DE IDs EN TABLA ventas")
    print("=" * 70)
    cursor.execute("SELECT MIN(id), MAX(id), COUNT(*) FROM ventas")
    row = cursor.fetchone()
    print(f"Min ID: {row[0]}")
    print(f"Max ID: {row[1]}")
    print(f"Total registros: {row[2]}")
    
    print("\n" + "=" * 70)
    print("ÚLTIMOS 5 IDs EN TABLA ventas")
    print("=" * 70)
    cursor.execute("SELECT id, usuario_id, total FROM ventas ORDER BY id DESC LIMIT 5")
    for row in cursor.fetchall():
        print(row)
