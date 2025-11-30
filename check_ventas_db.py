#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from ventas.models import Venta, VentaDetalle
from pagos.models import Payment

print("=" * 70)
print("VENTAS EN BASE DE DATOS - JAMEL")
print("=" * 70)

ventas = Venta.objects.filter(usuario__email='jamel@gmail.com')
print(f"Total ventas para jamel: {ventas.count()}\n")

for v in ventas:
    detalles_count = VentaDetalle.objects.filter(venta=v).count()
    print(f"Venta ID {v.id}")
    print(f"  Monto: Bs. {v.total}")
    print(f"  Fecha: {v.creado_en}")
    print(f"  Detalles: {detalles_count}")
    
    if detalles_count > 0:
        for d in VentaDetalle.objects.filter(venta=v):
            print(f"    - {d.producto.nombre} x{d.cantidad} @ Bs. {d.precio_unitario}")
    print()

print("=" * 70)
print("PAGOS EN BASE DE DATOS - ÚLTIMOS 10")
print("=" * 70)
for p in Payment.objects.all().order_by('-created_at')[:10]:
    print(f"Payment {p.id}: {p.amount_cents} cents | {p.stripe_session_id[:20]}... | {p.created_at}")
