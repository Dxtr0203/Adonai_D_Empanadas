#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from ventas.models import Venta
from django.db.models import Sum, Count

# Obtener rango de fechas
ventas = Venta.objects.all().order_by('creado_en')
if ventas:
    print(f"Primera venta: {ventas.first().creado_en}")
    print(f"Última venta: {ventas.last().creado_en}")
    print(f"Total ventas: {ventas.count()}")
    print(f"Ingresos totales: Bs. {ventas.aggregate(Sum('total'))['total__sum']:.2f}")
    
    # Contar por fecha
    ventas_por_fecha = ventas.values('creado_en__date').annotate(cantidad=Count('id'), total=Sum('total')).order_by('creado_en__date')
    print(f"\nPrimeras 10 fechas con ventas:")
    for v in ventas_por_fecha[:10]:
        print(f"  {v['creado_en__date']}: {v['cantidad']} ventas, Bs. {v['total']:.2f}")
else:
    print("No hay ventas")
