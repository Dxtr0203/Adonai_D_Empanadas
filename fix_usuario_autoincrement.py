#!/usr/bin/env python
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

with connection.cursor() as cursor:
    print("=" * 70)
    print("AGREGANDO AUTO_INCREMENT A TABLA usuarios")
    print("=" * 70)
    
    try:
        print("\n1. Modificando campo id...")
        cursor.execute("""
            ALTER TABLE usuarios 
            MODIFY COLUMN id BIGINT AUTO_INCREMENT
        """)
        print("   ✅ AUTO_INCREMENT agregado a usuarios.id")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n2. Verificando estructura...")
    cursor.execute("DESCRIBE usuarios")
    for row in cursor.fetchall():
        if row[0] == 'id':
            print(f"   {row[0]:20} {row[1]:20} {row[5]:30}")
