#!/usr/bin/env python
"""
Ver qué hay en los metadatos de las compras sin detalles
"""
import os
import django
import stripe
import json
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from django.conf import settings
from pagos.models import Payment
from ventas.models import Venta, VentaDetalle

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

# Obtener usuario jamel
from usuarios.models import Usuario
usuario = Usuario.objects.get(nombre='jamel')

# Obtener ventas de jamel sin detalles
print("=" * 80)
print("METADATOS DE COMPRAS SIN DETALLES")
print("=" * 80)

for venta in Venta.objects.filter(usuario=usuario):
    if VentaDetalle.objects.filter(venta=venta).count() == 0:
        print(f"\n📦 Venta ID {venta.id}:")
        
        # Buscar Payment cercano
        start_time = venta.creado_en - timedelta(minutes=5)
        end_time = venta.creado_en + timedelta(minutes=5)
        
        payment = Payment.objects.filter(
            created_at__gte=start_time,
            created_at__lte=end_time,
            amount_cents__gte=int(venta.total * 100) - 100,
            amount_cents__lte=int(venta.total * 100) + 100
        ).first()
        
        if payment:
            try:
                session = stripe.checkout.Session.retrieve(payment.stripe_session_id)
                cart_items = json.loads(session['metadata']['cart_items'])
                
                print(f"  Items en Stripe:")
                print(json.dumps(cart_items, indent=2))
            except:
                print("  Error obteniendo metadatos")

print("\n" + "=" * 80)
