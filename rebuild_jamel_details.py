#!/usr/bin/env python
"""
Script para reconstruir detalles faltantes de compras nuevas
"""
import os
import django
import stripe
import json
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from django.conf import settings
from decimal import Decimal
from pagos.models import Payment
from ventas.models import Venta, VentaDetalle
from productos.models import Producto

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

print("=" * 80)
print("RECONSTRUYENDO DETALLES FALTANTES - JAMEL")
print("=" * 80)

# Obtener usuario jamel
from usuarios.models import Usuario
usuario = Usuario.objects.get(nombre='jamel')

# Obtener ventas de jamel sin detalles
ventas_sin_detalles = []
for venta in Venta.objects.filter(usuario=usuario):
    if VentaDetalle.objects.filter(venta=venta).count() == 0:
        ventas_sin_detalles.append(venta)

print(f"\n📦 Ventas sin detalles: {len(ventas_sin_detalles)}")

for venta in ventas_sin_detalles:
    print(f"\n  Venta ID {venta.id} - Monto: Bs. {venta.total}")
    
    # Buscar Payment cercano
    start_time = venta.creado_en - timedelta(minutes=5)
    end_time = venta.creado_en + timedelta(minutes=5)
    
    payment = Payment.objects.filter(
        created_at__gte=start_time,
        created_at__lte=end_time,
        amount_cents__gte=int(venta.total * 100) - 100,
        amount_cents__lte=int(venta.total * 100) + 100
    ).first()
    
    if not payment:
        print(f"    ❌ Payment no encontrado")
        continue
    
    print(f"    ✅ Payment encontrado: {payment.stripe_session_id[:30]}...")
    
    try:
        session = stripe.checkout.Session.retrieve(payment.stripe_session_id)
        metadata = session.get('metadata', {})
        
        if not metadata.get('cart_items'):
            print(f"    ❌ Sin cart_items en metadatos")
            continue
        
        cart_items = json.loads(metadata['cart_items'])
        print(f"    📋 Items en Stripe: {len(cart_items)}")
        
        # Crear VentaDetalles
        for item in cart_items:
            try:
                product_id = item.get('id')
                product_name = item.get('nombre') or item.get('name')
                quantity = int(item.get('cantidad') or item.get('quantity', 1))
                precio_str = str(item.get('precio', 0)).replace(',', '.')
                price = Decimal(precio_str)
                
                print(f"      Procesando: ID={product_id}, Nombre={product_name}, Precio={precio_str}")
                
                # Obtener producto - verificar que product_id es válido
                producto = None
                if product_id:
                    try:
                        producto = Producto.objects.get(id=int(product_id))
                        print(f"      ✓ Producto encontrado por ID: {producto.nombre}")
                    except (Producto.DoesNotExist, ValueError):
                        print(f"      ✗ Producto ID {product_id} no existe, buscando por nombre...")
                        producto = Producto.objects.filter(nombre__iexact=product_name).first()
                else:
                    producto = Producto.objects.filter(nombre__iexact=product_name).first()
                
                if producto:
                    subtotal = price * quantity
                    print(f"      → Verificando: producto_id={producto.id}, cantidad={quantity}, precio={price}")
                    
                    # No pasar subtotal, se calcula automáticamente en BD
                    detalle = VentaDetalle.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=quantity,
                        precio_unitario=price,
                        # subtotal se calcula automáticamente
                    )
                    print(f"      ✅ {producto.nombre} x{quantity} = Bs. {subtotal}")
                else:
                    print(f"      ⚠️ Producto no encontrado: {product_name}")
                    
            except Exception as e:
                print(f"      ❌ Error: {type(e).__name__}: {e}")
    
    except Exception as e:
        print(f"    ❌ Error: {e}")

print("\n" + "=" * 80)
