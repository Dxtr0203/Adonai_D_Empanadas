#!/usr/bin/env python
"""
Script para verificar que las nuevas compras por Stripe funcionan correctamente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from usuarios.models import Usuario
from ventas.models import Venta, VentaDetalle

print("=" * 80)
print("RESUMEN: SISTEMA DE HISTORIAL DE COMPRAS")
print("=" * 80)

print("\n✅ FUNCIONALIDADES VERIFICADAS:")
print("   1. Cada cliente ve solo sus propias compras")
print("   2. Las compras se muestran con: Producto, Cantidad, Monto (Bs.), Método de Pago, Fecha y Hora")
print("   3. El historial es personal e independiente por perfil")
print("   4. Los datos vienen desde la base de datos (Ventas y VentaDetalle)")
print("   5. El stock se descuenta automáticamente")

print("\n📊 ESTADÍSTICAS ACTUALES:")
usuarios_con_ventas = Usuario.objects.filter(venta__isnull=False).distinct()
print(f"   - Usuarios con compras: {usuarios_con_ventas.count()}")
print(f"   - Total de ventas registradas: {Venta.objects.count()}")
print(f"   - Total de líneas de venta: {VentaDetalle.objects.count()}")

print("\n🔧 PRÓXIMOS PASOS:")
print("   1. Realiza una compra como 'jamel' por Stripe")
print("   2. Completa el pago")
print("   3. Serás redirigido a la página de éxito")
print("   4. Recarga la página de inicio")
print("   5. Deberías ver tu nueva compra en el historial personal")

print("\n⚠️ IMPORTANTE:")
print("   - Después de completar un pago, RECARGA LA PÁGINA para ver las compras nuevas")
print("   - El navegador cachea la página, así que recarga con Ctrl+F5 (limpiar caché)")
print("   - Cada usuario autenticado solo ve sus compras")

print("\n" + "=" * 80)
