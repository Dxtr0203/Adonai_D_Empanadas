#!/usr/bin/env python
import os
import json
import django
import stripe
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from django.conf import settings
from pagos.models import Payment
from ventas.models import Venta, VentaDetalle
from productos.models import Producto
from usuarios.models import Usuario
from django.db import connection

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

jamel = Usuario.objects.get(email='jamel@gmail.com')

# Ventas sin detalles
ventas_sin_detalles = []
for v in Venta.objects.filter(usuario=jamel):
    if VentaDetalle.objects.filter(venta=v).count() == 0:
        ventas_sin_detalles.append(v)

print("=" * 70)
print(f"OBTENER CART_ITEMS DESDE STRIPE - {len(ventas_sin_detalles)} Ventas")
print("=" * 70)

# Obtener el session_id de cada venta desde Payment
for venta in ventas_sin_detalles:
    print(f"\n📦 Venta {venta.id} - Bs. {venta.total}")
    
    # Buscar Payment con fecha cercana
    from datetime import timedelta
    fecha_min = venta.creado_en - timedelta(minutes=5)
    fecha_max = venta.creado_en + timedelta(minutes=5)
    
    payment = Payment.objects.filter(
        created_at__gte=fecha_min,
        created_at__lte=fecha_max
    ).first()
    
    if not payment:
        print(f"  ❌ Payment no encontrado")
        continue
    
    print(f"  ✅ Payment encontrado: {payment.stripe_session_id[:20]}...")
    
    try:
        # Obtener la sesión desde Stripe
        session = stripe.checkout.Session.retrieve(payment.stripe_session_id)
        
        cart_items = []
        if session.get('metadata', {}).get('cart_items'):
            try:
                cart_items = json.loads(session['metadata']['cart_items'])
                print(f"  📋 Items en Stripe: {len(cart_items)}")
            except:
                pass
        
        if not cart_items:
            print(f"  ⚠️ No hay cart_items en metadatos")
        else:
            # Reconstruir detalles
            for item in cart_items:
                product_id = item.get('id')
                quantity = item.get('cantidad') or item.get('quantity', 1)
                precio_str = str(item.get('precio', 0)).replace(',', '.')
                price = Decimal(precio_str)
                
                try:
                    producto = Producto.objects.get(id=product_id)
                    print(f"    ✓ {producto.nombre} x{quantity} @ Bs. {price}")
                    
                    # Calcular subtotal
                    subtotal = price * quantity
                    
                    # Insertar directamente en BD
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO ventas_ventadetalle 
                            (venta_id, producto_id, cantidad, precio_unitario, subtotal) 
                            VALUES (%s, %s, %s, %s, %s)
                        """, [venta.id, producto.id, quantity, price, subtotal])
                    
                    print(f"      → ✅ Creado en DB")
                
                except Producto.DoesNotExist:
                    print(f"    ❌ Producto ID {product_id} no existe")
                except Exception as e:
                    print(f"    ❌ Error insertando: {e}")
    
    except Exception as e:
        print(f"  ❌ Error obteniendo sesión Stripe: {e}")

print("\n" + "=" * 70)
print("VERIFICANDO DETALLES CREADOS...")
print("=" * 70)
for venta in ventas_sin_detalles:
    count = VentaDetalle.objects.filter(venta=venta).count()
    estado = "✅" if count > 0 else "❌"
    print(f"{estado} Venta {venta.id}: {count} detalles")
