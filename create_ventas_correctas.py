#!/usr/bin/env python
"""
Script para limpiar y crear ventas correctamente con fechas válidas
"""
import os
import django
from datetime import datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from ventas.models import Venta, VentaDetalle
from usuarios.models import Usuario
from productos.models import Producto
from django.db import connection
from django.utils import timezone

# Obtener datos
usuarios = list(Usuario.objects.filter(id__gt=0).order_by('?'))
productos = list(Producto.objects.all())

print(f"[*] Usuarios: {len(usuarios)}")
print(f"[*] Productos: {len(productos)}")

if not usuarios or not productos:
    print("[ERROR] No hay datos suficientes")
    exit(1)

# Limpiar todas las ventas
VentaDetalle.objects.all().delete()
Venta.objects.all().delete()
print("[OK] Todas las ventas eliminadas")

# Deshabilitar FK
with connection.cursor() as cursor:
    cursor.execute("SET FOREIGN_KEY_CHECKS=0")

try:
    fecha_inicio = datetime(2025, 10, 31, 7, 0, 0)
    fecha_fin = datetime(2025, 11, 30, 20, 0, 0)
    
    ventas_count = 0
    total_ingresos = 0.0
    dias_rango = (fecha_fin.date() - fecha_inicio.date()).days + 1
    
    print(f"[*] Creando ventas para {dias_rango} días...")
    
    for dia in range(dias_rango):
        fecha_actual = fecha_inicio + timedelta(days=dia)
        num_ventas_hoy = random.randint(4, 8)
        
        for v in range(num_ventas_hoy):
            usuario = random.choice(usuarios)
            hora = random.randint(7, 20)
            minuto = random.randint(0, 59)
            segundo = random.randint(0, 59)
            
            # Crear datetime consciente de zona horaria
            venta_datetime = timezone.make_aware(
                fecha_actual.replace(hour=hora, minute=minuto, second=segundo)
            )
            
            venta = Venta(
                usuario=usuario,
                total=0,
                metodo_pago=random.choice(['Efectivo', 'Tarjeta', 'Transferencia', 'Otro']),
                estado=random.choice(['pendiente', 'pagado', 'en_preparacion', 'entregado']),
                direccion_entrega="Calle " + str(random.randint(1, 999)),
                ciudad_entrega="La Paz",
                creado_en=venta_datetime
            )
            venta.save()
            
            total_venta = 0.0
            
            # Agregar 1-3 detalles
            num_items = random.randint(1, 3)
            for j in range(num_items):
                producto = random.choice(productos)
                cantidad = random.randint(1, 4)
                precio = float(producto.precio)
                subtotal = cantidad * precio
                total_venta += subtotal
                
                VentaDetalle.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio
                )
            
            venta.total = total_venta
            venta.save()
            
            ventas_count += 1
            total_ingresos += total_venta
    
    # Rehabilitar FK
    with connection.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
    
    print(f"\n[FINAL] {ventas_count} ventas creadas")
    print(f"[FINAL] Período: 31/10/2025 - 30/11/2025")
    print(f"[FINAL] Ingresos totales: Bs. {total_ingresos:.2f}")
    
    # Verificación
    from django.db.models import Count, Sum
    ventas_por_fecha = Venta.objects.values('creado_en__date').annotate(
        cantidad=Count('id'), total=Sum('total')
    ).order_by('creado_en__date')
    
    print(f"\n[VERIFICACION] Primeras 10 fechas:")
    for v in list(ventas_por_fecha)[:10]:
        print(f"  {v['creado_en__date']}: {v['cantidad']} ventas, Bs. {v['total']:.2f}")
    
except Exception as e:
    print(f"[ERROR]: {e}")
    import traceback
    traceback.print_exc()
finally:
    with connection.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
