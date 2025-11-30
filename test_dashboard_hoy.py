#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from ventas.models import Venta, VentaDetalle
from django.utils import timezone
from datetime import datetime, timedelta

hoy = timezone.localdate()
dt_hoy_inicio = timezone.make_aware(datetime.combine(hoy, datetime.min.time()))
dt_hoy_fin = timezone.make_aware(datetime.combine(hoy, datetime.max.time()))

print(f"\n{'='*60}")
print(f"REVISANDO HISTORIAL DE VENTAS DEL DÍA")
print(f"{'='*60}")
print(f"Hoy: {hoy}")
print(f"Rango: {dt_hoy_inicio} a {dt_hoy_fin}\n")

ventas_hoy = Venta.objects.filter(
    creado_en__gte=dt_hoy_inicio, 
    creado_en__lte=dt_hoy_fin
).select_related('usuario').prefetch_related('ventadetalle_set__producto').order_by('-creado_en')

print(f"Total de ventas encontradas: {ventas_hoy.count()}\n")

historial_ventas = []
for venta in ventas_hoy:
    detalles = []
    for detalle in venta.ventadetalle_set.all():
        detalles.append({
            'producto': detalle.producto.nombre,
            'cantidad': detalle.cantidad,
            'precio': float(detalle.precio_unitario),
            'subtotal': float(detalle.subtotal)
        })
    historial_ventas.append({
        'id': venta.id,
        'cliente': venta.usuario.nombre if venta.usuario else 'Cliente Anónimo',
        'email': venta.usuario.email if venta.usuario else '',
        'hora': venta.creado_en.strftime('%H:%M:%S'),
        'metodo_pago': venta.metodo_pago,
        'estado': venta.estado,
        'total': float(venta.total),
        'detalles': detalles
    })

print(f"Historial ventas procesado: {len(historial_ventas)} registros\n")

if historial_ventas:
    print("Primeras 5 ventas:")
    for i, v in enumerate(historial_ventas[:5], 1):
        print(f"{i}. ID:{v['id']} | {v['hora']} | {v['cliente']} | {len(v['detalles'])} items | Bs. {v['total']}")
        for d in v['detalles']:
            print(f"   - {d['cantidad']}x {d['producto']} = Bs. {d['subtotal']}")
else:
    print("❌ NO HAY VENTAS PARA MOSTRAR")

print(f"\n{'='*60}\n")
