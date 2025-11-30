#!/usr/bin/env python
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from usuarios.models import Usuario

jamel = Usuario.objects.get(email='jamel@gmail.com')

with connection.cursor() as cursor:
    print("=" * 70)
    print(f"VENTAS DE JAMEL (usuario_id={jamel.id}) - TABLA ventas_venta")
    print("=" * 70)
    cursor.execute("""
        SELECT id, usuario_id, total, metodo_pago, creado_en 
        FROM ventas_venta 
        WHERE usuario_id = %s
        ORDER BY id
    """, [jamel.id])
    
    for row in cursor.fetchall():
        venta_id = row[0]
        print(f"\nVenta ID {venta_id} - Bs. {row[2]} - Método: {row[3]}")
        
        # Ver detalles
        cursor.execute("""
            SELECT cantidad, precio_unitario, subtotal FROM ventas_ventadetalle 
            WHERE venta_id = %s
        """, [venta_id])
        
        detalles = cursor.fetchall()
        if detalles:
            total_qty = sum(d[0] for d in detalles)
            print(f"  ✅ {len(detalles)} item(s), {total_qty} unidades")
            for d in detalles:
                print(f"    - Qty: {d[0]:2} | Unit: Bs. {d[1]:7} | Subtotal: Bs. {d[2]}")
        else:
            print(f"  ❌ SIN DETALLES")
