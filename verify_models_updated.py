#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from ventas.models import Venta, VentaDetalle
from usuarios.models import Usuario

print("=" * 70)
print("VERIFICANDO MODELOS DESPUÉS DE ACTUALIZAR db_table")
print("=" * 70)

jamel = Usuario.objects.filter(email='jamel@gmail.com').first()
if not jamel:
    print("❌ Usuario jamel no encontrado")
else:
    print(f"✅ Usuario jamel encontrado: ID {jamel.id}")
    
    ventas = Venta.objects.filter(usuario=jamel)
    print(f"\n📦 Ventas de jamel: {ventas.count()}")
    
    for v in ventas:
        detalles_count = VentaDetalle.objects.filter(venta=v).count()
        print(f"\n  Venta ID {v.id}")
        print(f"    Monto: Bs. {v.total}")
        print(f"    Fecha: {v.creado_en}")
        print(f"    Detalles: {detalles_count}")
        
        if detalles_count > 0:
            for d in VentaDetalle.objects.filter(venta=v):
                print(f"      - {d.producto.nombre} x{d.cantidad} @ Bs. {d.precio_unitario}")
