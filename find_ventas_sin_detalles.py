#!/usr/bin/env python
"""
Script para reconstruir detalles de ventas sin VentaDetalle
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from ventas.models import Venta, VentaDetalle
from productos.models import Producto
from decimal import Decimal

print("=" * 80)
print("RECONSTRUYENDO DETALLES DE VENTAS")
print("=" * 80)

# Encontrar ventas sin detalles
ventas_sin_detalles = []
for venta in Venta.objects.all():
    detalles = VentaDetalle.objects.filter(venta=venta)
    if not detalles.exists():
        ventas_sin_detalles.append(venta)

print(f"\n📦 Ventas sin detalles encontradas: {len(ventas_sin_detalles)}")

for venta in ventas_sin_detalles:
    print(f"\n  Venta ID {venta.id}:")
    print(f"    Usuario: {venta.usuario}")
    print(f"    Total: Bs. {venta.total}")
    print(f"    Método: {venta.metodo_pago}")
    print(f"    Fecha: {venta.creado_en}")
    
    # Si tiene total pero sin detalles, intentamos recrear un detalle genérico
    if venta.total > 0 and not venta.usuario:
        print(f"    ⚠️ Venta sin usuario y sin detalles - REQUIERE INVESTIGACIÓN")
    elif venta.total > 0:
        print(f"    ⚠️ Sin detalles de productos")

print("\n" + "=" * 80)
