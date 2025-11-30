#!/usr/bin/env python
"""
Script para arreglar las fechas de creacion de las ventas
"""
import os
import django
from datetime import datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from ventas.models import Venta
from django.utils import timezone

# Obtener todas las ventas con fecha None
ventas_sin_fecha = Venta.objects.filter(creado_en__isnull=True)

if ventas_sin_fecha.exists():
    print(f"[*] Encontradas {ventas_sin_fecha.count()} ventas sin fecha válida")
    
    # Asignar fechas aleatorias entre 31/10/2025 y 30/11/2025
    fecha_inicio = timezone.make_aware(datetime(2025, 10, 31, 0, 0, 0))
    fecha_fin = timezone.make_aware(datetime(2025, 11, 30, 23, 59, 59))
    
    dias_rango = (fecha_fin - fecha_inicio).days
    
    for i, venta in enumerate(ventas_sin_fecha):
        dias_aleatorios = random.randint(0, dias_rango)
        horas_aleatorias = random.randint(7, 20)
        minutos_aleatorios = random.randint(0, 59)
        
        nueva_fecha = fecha_inicio + timedelta(days=dias_aleatorios, hours=horas_aleatorias, minutes=minutos_aleatorios)
        venta.creado_en = nueva_fecha
        venta.save()
        
        if (i + 1) % 50 == 0:
            print(f"[OK] {i + 1} ventas actualizadas...")
    
    print(f"[FINAL] {ventas_sin_fecha.count()} ventas corregidas con fechas válidas")
    
    # Verificar resultado
    from django.db.models import Sum, Count
    ventas_todas = Venta.objects.all()
    ventas_por_fecha = ventas_todas.values('creado_en__date').annotate(cantidad=Count('id'), total=Sum('total')).order_by('creado_en__date')
    print(f"\n[VERIFICACION] Primeras 10 fechas con ventas:")
    for v in ventas_por_fecha[:10]:
        print(f"  {v['creado_en__date']}: {v['cantidad']} ventas, Bs. {v['total']:.2f}")
else:
    print("[OK] Todas las ventas tienen fecha válida")
