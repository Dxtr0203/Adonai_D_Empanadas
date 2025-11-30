#!/usr/bin/env python
"""
Verificar integridad de la BD
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from django.db import connection
from productos.models import Producto

print("=" * 80)
print("VERIFICANDO INTEGRIDAD DE BD")
print("=" * 80)

# Verificar que los productos que encontramos en metadatos existen
product_ids = [8, 6, 3, 4, 19]

print("\n✓ Verificando productos:")
for pid in product_ids:
    p = Producto.objects.get(id=pid)
    print(f"  ID {pid}: {p.nombre} (Stock: {p.stock_actual})")

# Verificar si puedo crear un VentaDetalle directamente
print("\n✓ Verificando tabla productos_producto:")
with connection.cursor() as cursor:
    cursor.execute("SELECT id FROM productos_producto WHERE id IN (3, 4, 6, 8, 19)")
    rows = cursor.fetchall()
    print(f"  Productos encontrados en BD: {len(rows)}")
    for row in rows:
        print(f"    - ID {row[0]}")

print("\n" + "=" * 80)
