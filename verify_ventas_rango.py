#!/usr/bin/env python
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from ventas.models import Venta
from django.db.models import Sum, Count

# Rango de fechas
fecha_inicio = datetime(2025, 10, 31).date()
fecha_fin = datetime(2025, 11, 30).date()

print(f"Buscando ventas entre {fecha_inicio} y {fecha_fin}")

# Obtener ventas en el rango
ventas = Venta.objects.filter(creado_en__date__range=(fecha_inicio, fecha_fin))

print(f"Total ventas en rango: {ventas.count()}")
print(f"Ingresos en rango: Bs. {ventas.aggregate(Sum('total'))['total__sum'] or 0:.2f}")

# Contar por fecha
ventas_por_fecha = ventas.values('creado_en__date').annotate(cantidad=Count('id'), total=Sum('total')).order_by('creado_en__date')

print(f"\nVentas por fecha:")
for v in ventas_por_fecha:
    print(f"  {v['creado_en__date']}: {v['cantidad']} ventas, Bs. {v['total']:.2f}")
