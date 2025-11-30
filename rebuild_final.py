#!/usr/bin/env python
"""
Reconstruir detalles - insertar solo cantidad y precio_unitario
"""
import os
import django
import stripe
import json
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from django.conf import settings
from django.db import connection
from decimal import Decimal
from pagos.models import Payment
from ventas.models import Venta, VentaDetalle
from productos.models import Producto

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

print("=" * 80)
print("RECONSTRUYENDO - CON SQL DIRECTO (SIN SUBTOTAL)")
print("=" * 80)

# Obtener usuario jamel
from usuarios.models import Usuario
usuario = Usuario.objects.get(nombre='jamel')

# Obtener ventas de jamel sin detalles
for venta in Venta.objects.filter(usuario=usuario):
    if VentaDetalle.objects.filter(venta=venta).count() == 0:
        print(f"\n  Venta ID {venta.id}:")
        
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
            continue
        
        try:
            session = stripe.checkout.Session.retrieve(payment.stripe_session_id)
            cart_items = json.loads(session['metadata']['cart_items'])
            
            for item in cart_items:
                try:
                    product_name = item.get('nombre') or item.get('name')
                    quantity = int(item.get('cantidad') or item.get('quantity', 1))
                    precio_str = str(item.get('precio', 0)).replace(',', '.')
                    price = Decimal(precio_str)
                    
                    # Buscar por nombre exacto
                    producto = Producto.objects.filter(nombre=product_name).first()
                    
                    if not producto:
                        print(f"    ⚠️ Producto no encontrado: {product_name}")
                        continue
                    
                    # Insertar SIN subtotal - dejar que la BD lo calcule
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO venta_detalles 
                            (venta_id, producto_id, cantidad, precio_unitario) 
                            VALUES (%s, %s, %s, %s)
                        """, [venta.id, producto.id, quantity, price])
                    
                    print(f"    ✅ {producto.nombre} x{quantity} = Bs. {price * quantity}")
                    
                except Exception as e:
                    print(f"    ❌ Error: {e}")
        
        except Exception as e:
            print(f"    ❌ Error: {e}")

print("\n" + "=" * 80)
print("Verificando detalles creados...")
print("=" * 80)

for venta in Venta.objects.filter(usuario=usuario).order_by('-creado_en'):
    detalles = VentaDetalle.objects.filter(venta=venta)
    if detalles.count() > 0:
        print(f"\n✅ Venta {venta.id}: {detalles.count()} detalles")
        for d in detalles:
            print(f"   - {d.producto.nombre} x{d.cantidad}")

print("\n" + "=" * 80)
