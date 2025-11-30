#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from datetime import datetime
from decimal import Decimal
from django.utils import timezone
from ventas.models import Venta, VentaDetalle
from productos.models import Producto
from usuarios.models import Usuario

print("\n" + "="*70)
print("CREAR VENTA DE PRUEBA PARA VERIFICAR DASHBOARD")
print("="*70)

# Obtener un usuario cliente
usuario = Usuario.objects.filter(rol__nombre__iexact='Cliente').first()
if not usuario:
    print("❌ No hay clientes disponibles")
    exit(1)

print(f"✅ Usuario: {usuario.nombre} ({usuario.email})")

# Obtener algunos productos
productos = Producto.objects.filter(estado='activo')[:3]
if not productos:
    print("❌ No hay productos activos")
    exit(1)

print(f"✅ Productos disponibles: {len(productos)}")

# Crear una venta de prueba HOY
venta = Venta.objects.create(
    usuario=usuario,
    metodo_pago='Stripe',
    estado='pagado',
    total=Decimal('0'),
    creado_en=timezone.now()
)

print(f"\n✅ Venta creada: ID={venta.id}")
print(f"   Hora: {venta.creado_en.strftime('%H:%M:%S')}")

# Agregar detalles
total_venta = Decimal('0')
for i, producto in enumerate(productos, 1):
    cantidad = 2
    precio = Decimal(str(producto.precio))
    subtotal = cantidad * precio
    
    detalle = VentaDetalle.objects.create(
        venta=venta,
        producto=producto,
        cantidad=cantidad,
        precio_unitario=precio,
        subtotal=subtotal
    )
    
    total_venta += subtotal
    print(f"   Detalle {i}: {cantidad}x {producto.nombre} = Bs. {subtotal:.2f}")

# Actualizar total de la venta
venta.total = total_venta
venta.save()

print(f"\n✅ Total de la venta: Bs. {total_venta:.2f}")

print("\n" + "="*70)
print("VERIFICAR EN EL DASHBOARD:")
print("="*70)
print("Ve a http://localhost:8000/panel/dashboard/")
print("Deberías ver esta compra en la tabla 'Historial de Ventas (Hoy)'")
print("=" * 70 + "\n")
