#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Min, Max
from ventas.models import Venta

print("\n" + "="*70)
print("VERIFICACION FINAL - DASHBOARD CON NUEVOS FILTROS")
print("="*70)

# Simular exactamente lo que hace el dashboard
fecha_inicio = date(2025, 10, 31)
fecha_fin = date(2025, 11, 30)

# Crear datetimes como hace el dashboard ahora
dt_inicio = timezone.make_aware(datetime.combine(fecha_inicio, datetime.min.time()))
dt_fin = timezone.make_aware(datetime.combine(fecha_fin, datetime.max.time()))

print(f"\nRango de búsqueda:")
print(f"  Inicio: {dt_inicio}")
print(f"  Fin:    {dt_fin}")

# Query como hace el dashboard
ventas_rango = Venta.objects.filter(creado_en__gte=dt_inicio, creado_en__lte=dt_fin)
total_ventas_rango = ventas_rango.aggregate(total=Sum('total'))['total'] or 0
cantidad_ventas_rango = ventas_rango.count()

print(f"\n[RESULTADO]")
print(f"  Cantidad de ventas encontradas: {cantidad_ventas_rango}")
print(f"  Total ingresos: Bs. {float(total_ventas_rango):,.2f}")

# Mostrar distribución por día (como hace el dashboard)
print(f"\n[GRÁFICO VENTAS POR FECHA - Primeros 10 días]")
dias = (fecha_fin - fecha_inicio).days + 1
datos_grafico = []

for i in range(dias):
    fecha = fecha_inicio + timedelta(days=i)
    # Crear rango datetime para cada día
    dt_dia_inicio = timezone.make_aware(datetime.combine(fecha, datetime.min.time()))
    dt_dia_fin = timezone.make_aware(datetime.combine(fecha, datetime.max.time()))
    total = Venta.objects.filter(creado_en__gte=dt_dia_inicio, creado_en__lte=dt_dia_fin).aggregate(total=Sum('total'))['total'] or 0
    count = Venta.objects.filter(creado_en__gte=dt_dia_inicio, creado_en__lte=dt_dia_fin).count()
    
    datos_grafico.append({
        'fecha': fecha.strftime('%a %d'),
        'total': float(total),
        'count': count
    })
    
    if i < 10 and count > 0:
        print(f"  {fecha.strftime('%Y-%m-%d %a')}: {count} ventas, Bs. {float(total):,.2f}")

# Contar días con datos
dias_con_datos = sum(1 for d in datos_grafico if d['count'] > 0)
print(f"\nDías con datos: {dias_con_datos}/{dias}")

# Mostrar stats finales
stats = Venta.objects.aggregate(
    fecha_min=Min('creado_en'),
    fecha_max=Max('creado_en'),
    total=Sum('total'),
    count=Count('id')
)

print(f"\n[ESTADÍSTICAS GLOBALES]")
print(f"  Total ventas en BD: {stats['count']}")
print(f"  Rango de fechas: {stats['fecha_min'].date()} a {stats['fecha_max'].date()}")
print(f"  Total de ingresos: Bs. {float(stats['total'] or 0):,.2f}")

print(f"\n[ESTADO DEL DASHBOARD]")
if cantidad_ventas_rango > 0 and dias_con_datos > 5:
    print("  ✅ Dashboard FUNCIONANDO CORRECTAMENTE")
    print(f"  ✅ Gráfico 'Ventas por fecha' mostrará {dias_con_datos} puntos de datos")
    print(f"  ✅ KPI mostrará Bs. {float(total_ventas_rango):,.2f} en ingresos")
else:
    print("  ❌ Dashboard aún tiene problemas")

print("\n" + "="*70)
