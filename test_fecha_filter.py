#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db.models import Min, Max, Count, Sum
from ventas.models import Venta

fecha_inicio = date(2025, 10, 31)
fecha_fin = date(2025, 11, 30)

print("="*60)
print("TESTS DE FECHA FILTER")
print("="*60)

# Test 1: Con __date__range
print("\n[TEST 1] __date__range")
try:
    q1 = Venta.objects.filter(creado_en__date__range=(fecha_inicio, fecha_fin))
    print(f"✓ Query: {q1.count()} ventas")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Con __date__gte y __date__lte
print("\n[TEST 2] __date__gte y __date__lte")
try:
    q2 = Venta.objects.filter(creado_en__date__gte=fecha_inicio, creado_en__date__lte=fecha_fin)
    print(f"✓ Query: {q2.count()} ventas")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Con datetimes
print("\n[TEST 3] Con datetimes completos (__gte y __lte)")
try:
    dt_inicio = timezone.make_aware(datetime(2025, 10, 31, 0, 0, 0))
    dt_fin = timezone.make_aware(datetime(2025, 11, 30, 23, 59, 59))
    q3 = Venta.objects.filter(creado_en__gte=dt_inicio, creado_en__lte=dt_fin)
    print(f"✓ Query: {q3.count()} ventas")
    print(f"  Rango: {dt_inicio} a {dt_fin}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Ver qué fechas tenemos
print("\n[TEST 4] Rango de fechas en BD")
agg = Venta.objects.aggregate(
    fecha_min=Min('creado_en'),
    fecha_max=Max('creado_en'),
    count=Count('id')
)
print(f"Fechas en BD: {agg['fecha_min']} a {agg['fecha_max']}")
print(f"Total ventas: {agg['count']}")

# Test 5: Verificar si hay ventas en Nov
print("\n[TEST 5] Ventas específicas")
q_nov = Venta.objects.filter(creado_en__year=2025, creado_en__month=11)
print(f"Ventas en Nov 2025: {q_nov.count()}")

q_oct = Venta.objects.filter(creado_en__year=2025, creado_en__month=10)
print(f"Ventas en Oct 2025: {q_oct.count()}")

# Test 6: Mostrar primeras 5
print("\n[TEST 6] Primeras 5 ventas en BD:")
for v in Venta.objects.all()[:5]:
    print(f"  {v.id}: {v.creado_en} (fecha: {v.creado_en.date()})")

# Test 7: El filter que usa el dashboard
print("\n[TEST 7] Filter del dashboard (ventas_por_fecha loop)")
dias = (fecha_fin - fecha_inicio).days + 1
data_puntos = 0
for i in range(dias):
    fecha = fecha_inicio + timedelta(days=i)
    count = Venta.objects.filter(creado_en__date=fecha).count()
    if count > 0:
        total = Venta.objects.filter(creado_en__date=fecha).aggregate(Sum('total'))['total__sum']
        print(f"  {fecha}: {count} ventas, total: {total}")
        data_puntos += count

print(f"\nTotal puntos con datos: {data_puntos}")

print("\n" + "="*60)
