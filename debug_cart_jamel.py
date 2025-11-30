#!/usr/bin/env python
"""
Script para ver qué hay en los cart_items
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

# Payment de jamel
payment = Payment.objects.get(stripe_session_id__startswith='cs_test_a1zcwcwZ6ITKzoEJ')
session = stripe.checkout.Session.retrieve(payment.stripe_session_id)
cart_items = json.loads(session['metadata']['cart_items'])

print("=" * 80)
print("CART ITEMS DE JAMEL")
print("=" * 80)
print(json.dumps(cart_items, indent=2))
print("=" * 80)
