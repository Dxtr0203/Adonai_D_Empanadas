#!/usr/bin/env python
"""
Script para debuggear la sesión de Stripe de jamel
"""
import os
import django
import stripe
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from django.conf import settings
from pagos.models import Payment
from ventas.models import Venta, VentaDetalle

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

print("=" * 80)
print("DEBUGGING SESIÓN STRIPE - JAMEL")
print("=" * 80)

# Obtener la venta de jamel
venta = Venta.objects.filter(usuario__nombre='jamel').first()
if venta:
    print(f"\n✅ Venta encontrada: ID {venta.id}")
    print(f"   Método: {venta.metodo_pago}")
    
    # Buscar el payment correspondiente
    payment = Payment.objects.filter(status='paid').order_by('-created_at').first()
    if payment:
        print(f"\n✅ Payment encontrado: {payment.stripe_session_id}")
        
        try:
            stripe_session = stripe.checkout.Session.retrieve(payment.stripe_session_id)
            print(f"\n📋 SESIÓN STRIPE:")
            print(f"   ID: {stripe_session.id}")
            print(f"   Email: {stripe_session.get('customer_details', {}).get('email')}")
            print(f"   Metadata keys: {stripe_session.get('metadata', {}).keys()}")
            print(f"   Metadata: {stripe_session.get('metadata', {})}")
            
            if stripe_session.get('metadata', {}).get('cart_items'):
                print(f"\n✅ Cart items encontrados en metadatos:")
                cart_items = json.loads(stripe_session['metadata']['cart_items'])
                for item in cart_items:
                    print(f"   - {item}")
            else:
                print(f"\n❌ NO HAY CART_ITEMS EN METADATOS")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ No hay payment")
else:
    print("❌ No hay venta de jamel")

print("\n" + "=" * 80)
