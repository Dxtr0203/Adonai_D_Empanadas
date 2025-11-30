#!/usr/bin/env python
"""
Script de prueba: simular una compra nueva para jamel
"""
import os
import django
import json
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from usuarios.models import Usuario
from ventas.models import Venta, VentaDetalle
from productos.models import Producto
from django.utils import timezone

print("=" * 80)
print("PRUEBA: CREAR VENTA MANUAL PARA JAMEL")
print("=" * 80)

# Obtener usuario jamel
usuario = Usuario.objects.get(nombre='jamel')
print(f"\n✅ Usuario: {usuario.nombre} ({usuario.email})")

# Obtener un producto
producto = Producto.objects.first()
print(f"✅ Producto: {producto.nombre}")

# Crear venta
venta = Venta.objects.create(
    usuario=usuario,
    total=Decimal('50.00'),
    metodo_pago='Stripe',
    estado='pagado',
    creado_en=timezone.now()
)
print(f"✅ Venta creada: ID {venta.id}")

# Crear detalle
detalle = VentaDetalle.objects.create(
    venta=venta,
    producto=producto,
    cantidad=2,
    precio_unitario=Decimal('25.00'),
    subtotal=Decimal('50.00')
)
print(f"✅ Detalle creado: {producto.nombre} x2")

# Verificar desde la vista
print(f"\n📊 Verificando desde core.views:")
from core.views import inicio

class MockRequest:
    def __init__(self, user):
        self.user = user
        self.is_authenticated = True

mock_request = MockRequest(user=usuario)

# Simular lo que hace core/views.py
historial_compras = []
if mock_request.user:
    try:
        usuario_local = Usuario.objects.get(email__iexact=mock_request.user.email)
        ventas = Venta.objects.filter(usuario=usuario_local).order_by('-creado_en')
        
        for v in ventas:
            detalles = VentaDetalle.objects.filter(venta=v)
            for detalle_item in detalles:
                historial_compras.append({
                    'producto': detalle_item.producto.nombre,
                    'cantidad': detalle_item.cantidad,
                    'precio_unitario': detalle_item.precio_unitario,
                    'subtotal': detalle_item.subtotal,
                    'metodo_pago': v.metodo_pago,
                    'creado_en': v.creado_en,
                    'estado': v.estado,
                })
    except Usuario.DoesNotExist:
        pass

print(f"✅ Historial recuperado: {len(historial_compras)} items")
for item in historial_compras:
    print(f"   - {item['producto']} x{item['cantidad']} = Bs. {item['subtotal']}")

print("\n" + "=" * 80)
