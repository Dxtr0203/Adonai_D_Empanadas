#!/usr/bin/env python
"""
Script para encontrar el Payment asociado a la venta de jamel
"""
import os
import django
import stripe
import json
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from django.conf import settings
from django.utils import timezone
from pagos.models import Payment
from ventas.models import Venta, VentaDetalle
from usuarios.models import Usuario

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

print("=" * 80)
print("BUSCANDO PAYMENT PARA VENTA DE JAMEL")
print("=" * 80)

# Venta de jamel
venta = Venta.objects.get(id=1741)
print(f"\n📦 Venta de jamel:")
print(f"   ID: {venta.id}")
print(f"   Fecha: {venta.creado_en}")
print(f"   Total: {venta.total}")

# Buscar Payment creado alrededor de esa fecha (±2 minutos)
start_time = venta.creado_en - timedelta(minutes=2)
end_time = venta.creado_en + timedelta(minutes=2)

payments_cercanos = Payment.objects.filter(
    created_at__gte=start_time,
    created_at__lte=end_time
).order_by('-created_at')

print(f"\n💳 Payments cercanos a esa fecha:")
if payments_cercanos:
    for p in payments_cercanos:
        print(f"   - Session: {p.stripe_session_id}")
        print(f"     Monto: {p.amount_cents} {p.currency}")
        print(f"     Estado: {p.status}")
        print(f"     Creado: {p.created_at}")
        
        # Revisar los metadatos
        try:
            session = stripe.checkout.Session.retrieve(p.stripe_session_id)
            cart_items = json.loads(session.get('metadata', {}).get('cart_items', '[]'))
            print(f"     Items en Stripe: {len(cart_items)}")
            for item in cart_items:
                print(f"       - {item.get('nombre')} x{item.get('cantidad')}")
        except Exception as e:
            print(f"     Error: {e}")
else:
    print("   ❌ No hay payments cercanos")

# Ahora vamos a encontrar TODOS los payments con status = created
# y mostrar los últimos 3
print(f"\n💳 Últimos 3 Payments con status=created:")
recent_payments = Payment.objects.filter(status='created').order_by('-created_at')[:3]
for p in recent_payments:
    print(f"   - {p.stripe_session_id[:30]}... (${p.amount_cents/100:.2f})")

print("\n" + "=" * 80)
