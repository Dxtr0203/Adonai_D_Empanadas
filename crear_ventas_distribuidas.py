#!/usr/bin/env python
import os
import django
import random
from datetime import datetime, date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from django.utils import timezone
from django.db.models import Count
from ventas.models import Venta, VentaDetalle
from productos.models import Producto
from usuarios.models import Usuario

print("\n" + "="*70)
print("CREAR VENTAS CORRECTAS CON FECHAS DISTRIBUIDAS (Oct 31 - Nov 30)")
print("="*70)

# Obtener datos
usuarios = list(Usuario.objects.filter(rol__nombre__iexact='Cliente'))
productos = list(Producto.objects.filter(estado='activo'))

print(f"\n[*] Usuarios clientes: {len(usuarios)}")
print(f"[*] Productos activos: {len(productos)}")

if not usuarios or not productos:
    print("❌ No hay usuarios o productos")
    exit(1)

# Eliminar ventas previas
print("\n[*] Eliminando ventas previas...")
Venta.objects.all().delete()
print("[OK] Todas las ventas eliminadas")

# Crear ventas para cada día del rango (Oct 31 - Nov 30)
fecha_inicio = date(2025, 10, 31)
fecha_fin = date(2025, 11, 30)
dias_totales = (fecha_fin - fecha_inicio).days + 1

print(f"\n[*] Creando ventas para {dias_totales} días...")

contador = 0
total_ingresos = 0.0
timezone_local = timezone.get_current_timezone()

for dia_offset in range(dias_totales):
    fecha_actual = fecha_inicio + timedelta(days=dia_offset)
    
    # 4-8 ventas por día (aleatorio)
    num_ventas_hoy = random.randint(4, 8)
    
    for _ in range(num_ventas_hoy):
        # Hora aleatoria del día (entre 8am y 8pm)
        hora = random.randint(8, 20)
        minuto = random.randint(0, 59)
        
        # Crear datetime con timezone
        dt_naive = datetime(
            fecha_actual.year,
            fecha_actual.month,
            fecha_actual.day,
            hora,
            minuto,
            0
        )
        dt_aware = timezone.make_aware(dt_naive)
        
        # Cliente aleatorio
        cliente = random.choice(usuarios)
        
        # Crear venta SIN creado_en (por ahora)
        venta = Venta.objects.create(
            usuario=cliente,
            metodo_pago=random.choice(['Efectivo', 'Tarjeta', 'Transferencia']),
            estado='pagado'
        )
        
        # Actualizar la fecha después de crear
        Venta.objects.filter(id=venta.id).update(creado_en=dt_aware)
        
        # 1-3 detalles por venta
        num_detalles = random.randint(1, 3)
        productos_elegidos = random.sample(productos, min(num_detalles, len(productos)))
        
        for producto in productos_elegidos:
            # Verificar que el producto existe
            if not Producto.objects.filter(id=producto.id).exists():
                continue
                
            cantidad = random.randint(1, 4)
            precio_unitario = float(producto.precio)
            subtotal = cantidad * precio_unitario
            
            try:
                VentaDetalle.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    subtotal=subtotal
                )
            except Exception as e:
                print(f"Error al crear detalle: {e}")
                continue
            
            venta.total += subtotal
        
        venta.save()
        contador += 1
        total_ingresos += venta.total

print(f"\n[OK] {contador} ventas creadas")
print(f"[FINAL] Período: {fecha_inicio} - {fecha_fin}")
print(f"[FINAL] Ingresos totales: Bs. {total_ingresos:,.2f}")

# Verificación
print("\n" + "="*70)
print("VERIFICACIÓN")
print("="*70)

from django.db.models import Sum, Count, Min, Max

# Test con __date__range
fecha_inicio_date = date(2025, 10, 31)
fecha_fin_date = date(2025, 11, 30)

print(f"\n[TEST] __date__range({fecha_inicio_date}, {fecha_fin_date})")
q_range = Venta.objects.filter(creado_en__date__range=(fecha_inicio_date, fecha_fin_date))
print(f"  Encontró: {q_range.count()} ventas")

# Test con datetimes
print(f"\n[TEST] Con datetimes")
dt_inicio = timezone.make_aware(datetime(2025, 10, 31, 0, 0, 0))
dt_fin = timezone.make_aware(datetime(2025, 11, 30, 23, 59, 59))
q_dt = Venta.objects.filter(creado_en__gte=dt_inicio, creado_en__lte=dt_fin)
print(f"  Encontró: {q_dt.count()} ventas")

# Estadísticas
stats = Venta.objects.aggregate(
    fecha_min=Min('creado_en'),
    fecha_max=Max('creado_en'),
    total=Sum('total'),
    count=Count('id')
)
print(f"\n[STATS]")
print(f"  Total ventas en BD: {stats['count']}")
print(f"  Fecha primera: {stats['fecha_min']}")
print(f"  Fecha última: {stats['fecha_max']}")
print(f"  Total ingresos: Bs. {float(stats['total'] or 0):,.2f}")

# Mostrar distribución por día
print(f"\n[DISTRIBUCIÓN POR FECHA]")
desde = date(2025, 10, 31)
hasta = date(2025, 11, 30)
dias = (hasta - desde).days + 1
puntos_con_datos = 0

for i in range(dias):
    fecha = desde + timedelta(days=i)
    count = Venta.objects.filter(creado_en__date=fecha).count()
    if count > 0:
        total = Venta.objects.filter(creado_en__date=fecha).aggregate(Sum('total'))['total__sum'] or 0
        print(f"  {fecha}: {count} ventas, Bs. {float(total):,.2f}")
        puntos_con_datos += 1

print(f"\nDías con datos: {puntos_con_datos}/{dias}")

print("\n" + "="*70)
