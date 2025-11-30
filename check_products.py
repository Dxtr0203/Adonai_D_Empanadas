#!/usr/bin/env python
"""
Ver qué productos existen en la BD
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from productos.models import Producto

print("=" * 80)
print("PRODUCTOS EN LA BASE DE DATOS")
print("=" * 80)

# Verificar IDs específicos
ids_faltantes = [8, 6, 3, 4, 19]

for product_id in ids_faltantes:
    try:
        p = Producto.objects.get(id=product_id)
        print(f"✅ ID {product_id}: {p.nombre}")
    except Producto.DoesNotExist:
        print(f"❌ ID {product_id}: NO EXISTE")

print(f"\n📊 Total de productos en BD: {Producto.objects.count()}")
print("\nPrimeros 10 productos:")
for p in Producto.objects.all()[:10]:
    print(f"  - ID {p.id}: {p.nombre}")

print("\n" + "=" * 80)
