#!/usr/bin/env python
"""
Script para debuggear las ventas en la base de datos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from usuarios.models import Usuario
from ventas.models import Venta, VentaDetalle
from pagos.models import Payment

print("=" * 80)
print("DEBUGGING VENTAS - BASE DE DATOS")
print("=" * 80)

# Listar todos los usuarios
print("\n📋 USUARIOS EN EL SISTEMA:")
usuarios = Usuario.objects.all()
for u in usuarios:
    print(f"  - {u.id}: {u.nombre} ({u.email})")

# Listar todas las ventas
print("\n📦 VENTAS REGISTRADAS:")
ventas = Venta.objects.all()
if ventas:
    for v in ventas:
        print(f"\n  Venta ID {v.id}:")
        print(f"    Usuario: {v.usuario}")
        print(f"    Total: Bs. {v.total}")
        print(f"    Método: {v.metodo_pago}")
        print(f"    Estado: {v.estado}")
        print(f"    Fecha: {v.creado_en}")
        
        # Detalles
        detalles = VentaDetalle.objects.filter(venta=v)
        for d in detalles:
            print(f"      - {d.producto.nombre} x{d.cantidad} = Bs. {d.subtotal}")
else:
    print("  ❌ NO HAY VENTAS")

# Listar pagos
print("\n💳 PAGOS REGISTRADOS:")
pagos = Payment.objects.all()
if pagos:
    for p in pagos:
        print(f"  - Session: {p.stripe_session_id}")
        print(f"    Monto: {p.amount_cents} centavos")
        print(f"    Moneda: {p.currency}")
        print(f"    Estado: {p.status}")
else:
    print("  ❌ NO HAY PAGOS")

print("\n" + "=" * 80)
