#!/usr/bin/env python
"""
Script para debuggear ventas del usuario jamel
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from usuarios.models import Usuario
from ventas.models import Venta, VentaDetalle

print("=" * 80)
print("DEBUGGING VENTAS - USUARIO JAMEL")
print("=" * 80)

# Buscar usuario jamel
try:
    usuario_jamel = Usuario.objects.get(nombre='jamel')
    print(f"\n✅ Usuario encontrado:")
    print(f"  ID: {usuario_jamel.id}")
    print(f"  Nombre: {usuario_jamel.nombre}")
    print(f"  Email: {usuario_jamel.email}")
    print(f"  Rol: {usuario_jamel.rol}")
    
    # Obtener sus ventas
    ventas_jamel = Venta.objects.filter(usuario=usuario_jamel).order_by('-creado_en')
    print(f"\n📦 Ventas de {usuario_jamel.nombre}:")
    
    if ventas_jamel:
        for v in ventas_jamel:
            print(f"\n  Venta ID {v.id}:")
            print(f"    Total: Bs. {v.total}")
            print(f"    Método: {v.metodo_pago}")
            print(f"    Estado: {v.estado}")
            print(f"    Fecha: {v.creado_en}")
            
            detalles = VentaDetalle.objects.filter(venta=v)
            for d in detalles:
                print(f"      - {d.producto.nombre} x{d.cantidad} = Bs. {d.subtotal}")
    else:
        print("  ❌ NO HAY VENTAS")
        
except Usuario.DoesNotExist:
    print("❌ Usuario 'jamel' no encontrado")

print("\n" + "=" * 80)
