#!/usr/bin/env python
"""
Script para verificar si hay sessions de Stripe con metadatos
"""
import os
import django
import stripe
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from django.conf import settings
from pagos.models import Payment

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

print("=" * 80)
print("VERIFICANDO SESIONES STRIPE - ÚLTIMAS 5")
print("=" * 80)

# Obtener últimos 5 pagos
payments = Payment.objects.all().order_by('-created_at')[:5]

for payment in payments:
    print(f"\n📦 Payment ID: {payment.id}")
    print(f"   Session: {payment.stripe_session_id}")
    print(f"   Estado: {payment.status}")
    print(f"   Monto: {payment.amount_cents} {payment.currency}")
    
    try:
        session = stripe.checkout.Session.retrieve(payment.stripe_session_id)
        print(f"   ✅ Session recuperada")
        
        # Revisar metadatos
        metadata = session.get('metadata', {})
        if metadata:
            print(f"   📋 Metadatos encontrados:")
            for key, value in metadata.items():
                if key == 'cart_items':
                    try:
                        items = json.loads(value)
                        print(f"      - {key}: {len(items)} items")
                        for item in items[:2]:  # Mostrar primeros 2
                            print(f"        - {item.get('nombre')} x{item.get('cantidad')}")
                    except:
                        print(f"      - {key}: [error parsing]")
                else:
                    print(f"      - {key}: {value}")
        else:
            print(f"   ❌ Sin metadatos")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
