#!/usr/bin/env python
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

with connection.cursor() as cursor:
    print("=" * 70)
    print("CONTENIDO pagos_payment")
    print("=" * 70)
    cursor.execute("""
        SELECT id, stripe_session_id, amount_cents, status, LENGTH(raw_event) as event_size
        FROM pagos_payment
        ORDER BY id DESC
        LIMIT 10
    """)
    for row in cursor.fetchall():
        print(f"ID {row[0]:3} | {row[1][:15]:15} | Amount: {row[2]:6} | {row[3]:8} | Event size: {row[4]}")
    
    print("\n" + "=" * 70)
    print("PRIMER raw_event (primeros 500 chars)")
    print("=" * 70)
    cursor.execute("SELECT id, raw_event FROM pagos_payment ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    if result and result[1]:
        print(f"ID: {result[0]}")
        print(result[1][:500])
    else:
        print("No hay raw_event")
