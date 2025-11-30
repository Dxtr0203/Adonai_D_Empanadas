#!/usr/bin/env python
import os
import json
import django
from datetime import datetime, timedelta
from django.db import connection
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from ventas.models import Venta, VentaDetalle
from pagos.models import Payment
from productos.models import Producto

print("=" * 70)
print("RECONSTRUYENDO DETALLES FALTANTES - VERSIÓN 3")
print("=" * 70)

# Encontrar ventas sin detalles
ventas_sin_detalles = []
for v in Venta.objects.filter(usuario__email='jamel@gmail.com'):
    if VentaDetalle.objects.filter(venta=v).count() == 0:
        ventas_sin_detalles.append(v)

print(f"\n📦 Ventas sin detalles: {len(ventas_sin_detalles)}\n")

for venta in ventas_sin_detalles:
    print(f"  Venta ID {venta.id} - Monto: Bs. {venta.total}")
    
    # Buscar Payment correspondiente (dentro de 5 minutos)
    fecha_min = venta.creado_en - timedelta(minutes=5)
    fecha_max = venta.creado_en + timedelta(minutes=5)
    
    payments = Payment.objects.filter(
        created_at__gte=fecha_min,
        created_at__lte=fecha_max
    )
    
    if not payments:
        print(f"    ❌ Payment no encontrado\n")
        continue
    
    payment = payments.first()
    print(f"    ✅ Payment encontrado: {payment.stripe_session_id[:20]}...")
    
    # Obtener cart_items de Stripe
    if not payment.raw_event:
        print(f"    ⚠️ raw_event vacío\n")
        continue
    
    try:
        event_data = json.loads(payment.raw_event)
        line_items = event_data.get('session', {}).get('display_items', [])
        
        if not line_items:
            print(f"    ⚠️ No hay line_items\n")
            continue
        
        print(f"    📋 Items en Stripe: {len(line_items)}")
        
        created_count = 0
        for item in line_items:
            # Obtener datos del item
            product_id = item.get('custom_price', {}).get('product', None)
            if not product_id:
                # Intentar extraer ID de other_price
                product_id = item.get('other_price', {}).get('product', None)
            
            if not product_id:
                print(f"      ⚠️ Product ID no encontrado en item")
                continue
            
            quantity = item.get('quantity', 1)
            price_str = str(item.get('custom_price', {}).get('unit_amount_decimal') or 
                          item.get('other_price', {}).get('unit_amount_decimal', 0))
            
            # Convertir precio a Decimal (cents a bs)
            if price_str:
                price_cents = int(Decimal(price_str))
                price = Decimal(price_cents) / Decimal('100')
            else:
                price = Decimal('0')
            
            # Buscar producto
            try:
                producto = Producto.objects.get(id=product_id)
                print(f"      ✓ ID={product_id}, Nombre={producto.nombre}, Qty={quantity}, Precio={price}")
                
                # Crear VentaDetalle
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO ventas_ventadetalle 
                        (venta_id, producto_id, cantidad, precio_unitario) 
                        VALUES (%s, %s, %s, %s)
                    """, [venta.id, producto.id, quantity, price])
                
                created_count += 1
                print(f"        → ✅ Creado en DB")
            
            except Producto.DoesNotExist:
                print(f"      ❌ Producto ID {product_id} no existe")
            except Exception as e:
                print(f"      ❌ Error insertando: {e}")
        
        print(f"    → {created_count} detalles creados\n")
    
    except json.JSONDecodeError:
        print(f"    ❌ Error decodificando raw_event\n")

print("=" * 70)
print("VERIFICANDO DETALLES CREADOS...")
print("=" * 70)
for venta in ventas_sin_detalles:
    count = VentaDetalle.objects.filter(venta=venta).count()
    estado = "✅" if count > 0 else "❌"
    print(f"{estado} Venta {venta.id}: {count} detalles")
