#!/usr/bin/env python
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

with connection.cursor() as cursor:
    print("=" * 70)
    print("ESTRUCTURA TABLA usuarios")
    print("=" * 70)
    cursor.execute("DESCRIBE usuarios")
    for row in cursor.fetchall():
        print(row)
    
    print("\n" + "=" * 70)
    print("ESTRUCTURA TABLA auth_user")
    print("=" * 70)
    cursor.execute("DESCRIBE auth_user")
    for row in cursor.fetchall():
        if row[0] in ['id', 'username', 'email']:
            print(row)
