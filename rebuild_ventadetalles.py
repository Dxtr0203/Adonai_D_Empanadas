#!/usr/bin/env python
"""
Script para reconstruir VentaDetalles desde metadatos de Stripe
"""
import os
import django
import stripe
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from django.conf import settings
from decimal import Decimal
from pagos.models import Payment
from ventas.models import Venta, VentaDetalle
from productos.models import Producto

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

print("=" * 80)
print("RECONSTRUYENDO VENTADETALLES DESDE STRIPE")
print("=" * 80)

# Obtener todas las ventas sin detalles
ventas_sin_detalles = []
for venta in Venta.objects.all():
    detalles = VentaDetalle.objects.filter(venta=venta)
    if not detalles.exists() and venta.total > 0:
        ventas_sin_detalles.append(venta)

print(f"\n📦 Ventas sin detalles a reconstruir: {len(ventas_sin_detalles)}")

for venta in ventas_sin_detalles:
    print(f"\n  Venta ID {venta.id} - Usuario: {venta.usuario}")
    
    # Si es método Stripe, buscar el Payment
    if venta.metodo_pago == 'Stripe':
        # Buscar Payment por fecha
        from datetime import timedelta
        start_time = venta.creado_en - timedelta(minutes=5)
        end_time = venta.creado_en + timedelta(minutes=5)
        
        payment = Payment.objects.filter(
            created_at__gte=start_time,
            created_at__lte=end_time,
            amount_cents__gte=int(venta.total * 100) - 100,  # ±Bs.1
            amount_cents__lte=int(venta.total * 100) + 100
        ).first()
        
        if payment:
            print(f"    ✅ Payment encontrado: {payment.stripe_session_id[:30]}...")
            
            try:
                # Obtener sesión de Stripe
                session = stripe.checkout.Session.retrieve(payment.stripe_session_id)
                metadata = session.get('metadata', {})
                
                if metadata.get('cart_items'):
                    cart_items = json.loads(metadata['cart_items'])
                    print(f"    📋 Items encontrados: {len(cart_items)}")
                    
                    # Crear VentaDetalles
                    for item in cart_items:
                        try:
                            product_id = item.get('id')
                            product_name = item.get('nombre') or item.get('name')
                            quantity = int(item.get('cantidad') or item.get('quantity', 1))
                            # Convertir precio: reemplazar coma por punto (localización)
                            precio_str = str(item.get('precio', 0)).replace(',', '.')
                            price = Decimal(precio_str)
                            
                            # Obtener producto
                            if product_id:
                                producto = Producto.objects.get(id=product_id)
                            else:
                                producto = Producto.objects.filter(nombre__icontains=product_name).first()
                            
                            if producto:
                                subtotal = price * quantity
                                detalle = VentaDetalle.objects.create(
                                    venta=venta,
                                    producto=producto,
                                    cantidad=quantity,
                                    precio_unitario=price,
                                    subtotal=subtotal
                                )
                                print(f"      ✅ {producto.nombre} x{quantity} = Bs. {subtotal}")
                            else:
                                print(f"      ❌ Producto no encontrado: {product_name}")
                                
                        except Exception as e:
                            print(f"      ❌ Error: {e}")
                else:
                    print(f"    ❌ Sin cart_items en metadatos")
                    
            except Exception as e:
                print(f"    ❌ Error recuperando sesión: {e}")
        else:
            print(f"    ❌ Payment no encontrado")

print("\n" + "=" * 80)
print("RECONSTRUCCIÓN COMPLETADA")
print("=" * 80)
