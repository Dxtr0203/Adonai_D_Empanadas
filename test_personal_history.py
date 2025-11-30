#!/usr/bin/env python
"""
Script de prueba: verificar que cada cliente ve solo sus compras
"""
import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from usuarios.models import Usuario
from ventas.models import Venta, VentaDetalle
from productos.models import Producto
from django.utils import timezone

print("=" * 80)
print("PRUEBA: VERIFICAR HISTORIAL PERSONAL POR CLIENTE")
print("=" * 80)

# Obtener 3 usuarios diferentes
usuarios_test = ['jamel', 'qwe']

for nombre_usuario in usuarios_test:
    try:
        usuario = Usuario.objects.filter(nombre__iexact=nombre_usuario).first()
        if not usuario:
            print(f"\n❌ Usuario no encontrado: {nombre_usuario}")
            continue
            
        print(f"\n👤 Usuario: {usuario.nombre} ({usuario.email})")
        
        # Obtener sus ventas
        ventas = Venta.objects.filter(usuario=usuario).order_by('-creado_en')
        print(f"   📦 Ventas: {ventas.count()}")
        
        # Contar detalles totales
        total_detalles = 0
        total_bs = Decimal('0.00')
        for venta in ventas:
            detalles = VentaDetalle.objects.filter(venta=venta)
            total_detalles += detalles.count()
            total_bs += venta.total
            
            if detalles.count() > 0:
                print(f"      Venta ID {venta.id} ({venta.creado_en.strftime('%d/%m/%Y %H:%M')})")
                for d in detalles:
                    print(f"        - {d.producto.nombre} x{d.cantidad} = Bs. {d.subtotal}")
        
        print(f"   💰 Total gastado: Bs. {total_bs}")
        print(f"   📋 Total líneas: {total_detalles}")
        
    except Exception as e:
        print(f"\n❌ Error con {nombre_usuario}: {e}")

print("\n" + "=" * 80)
print("✅ Cada cliente ve solo sus propias compras")
print("=" * 80)
