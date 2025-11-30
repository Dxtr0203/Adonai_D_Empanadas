#!/usr/bin/env python
"""
Script para debuggear detalles de compras
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from usuarios.models import Usuario
from ventas.models import Venta, VentaDetalle

# Obtener usuario jamel
usuario = Usuario.objects.get(nombre='jamel')
print("=" * 80)
print(f"DEBUGGING DETALLES - USUARIO: {usuario.nombre}")
print("=" * 80)

# Obtener ventas
ventas = Venta.objects.filter(usuario=usuario).order_by('-creado_en')

for idx, venta in enumerate(ventas, 1):
    print(f"\n📦 COMPRA #{idx} (Venta ID {venta.id}):")
    print(f"   Fecha: {venta.creado_en}")
    print(f"   Monto: Bs. {venta.total}")
    
    # Obtener detalles con select_related
    detalles = VentaDetalle.objects.filter(venta=venta).select_related('producto')
    
    print(f"   Detalles: {detalles.count()}")
    
    if detalles.count() == 0:
        print(f"   ❌ SIN DETALLES")
    else:
        for d in detalles:
            print(f"      ✅ {d.producto.nombre if d.producto else 'PRODUCTO NULO'}")
            print(f"         - Producto ID: {d.producto_id}")
            print(f"         - Producto objeto: {d.producto}")
            print(f"         - Cantidad: {d.cantidad}")
            print(f"         - Subtotal: {d.subtotal}")

print("\n" + "=" * 80)
