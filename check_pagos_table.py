#!/usr/bin/env python
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

with connection.cursor() as cursor:
    print("=" * 70)
    print("ESTRUCTURA TABLA pagos")
    print("=" * 70)
    cursor.execute("DESCRIBE pagos")
    for row in cursor.fetchall():
        print(row)
    
    print("\n" + "=" * 70)
    print("CONTENIDO TABLA pagos (primeros 5)")
    print("=" * 70)
    cursor.execute("SELECT id, stripe_session_id, amount_cents, status FROM pagos LIMIT 5")
    for row in cursor.fetchall():
        print(row)
    
    print("\n" + "=" * 70)
    print("raw_event SIZE")
    print("=" * 70)
    cursor.execute("SELECT id, stripe_session_id, LENGTH(raw_event) as size FROM pagos LIMIT 10")
    for row in cursor.fetchall():
        print(f"ID {row[0]}: {row[1][:20]}... | Size: {row[2]} bytes")
