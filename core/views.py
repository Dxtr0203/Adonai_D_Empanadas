# core/views.py
from django.shortcuts import render, redirect
from ventas.models import Venta, VentaDetalle
from usuarios.models import Usuario


def inicio(request):
    """Página de inicio pública para clientes.

    Ahora pública: no redirige al login automáticamente. Si el usuario está
    autenticado verá el menú de usuario en el header; si no, verá el botón
    "Registrarse".
    """
    historial_compras = []
    if request.user.is_authenticated:
        try:
            # Obtener el usuario personalizado
            usuario = Usuario.objects.get(email__iexact=request.user.email)
            
            # Obtener todas las ventas del usuario ordenadas por fecha más reciente
            # Usar select_related para optimizar queries
            ventas = Venta.objects.filter(usuario=usuario).order_by('-creado_en')
            
            # Construir historial con resumen de compras
            for idx, venta in enumerate(ventas, 1):
                # Obtener detalles con select_related al producto
                detalles = VentaDetalle.objects.filter(venta=venta).select_related('producto')
                
                # Calcular totales
                cantidad_total = sum(d.cantidad for d in detalles)
                
                # Construir lista de detalles para la modal
                detalles_list = []
                for detalle in detalles:
                    detalles_list.append({
                        'producto': detalle.producto.nombre if detalle.producto else 'Producto no disponible',
                        'cantidad': detalle.cantidad,
                        'precio_unitario': detalle.precio_unitario,
                        'subtotal': detalle.subtotal,
                    })
                
                historial_compras.append({
                    'numero_compra': idx,
                    'venta_id': venta.id,
                    'cantidad_total': cantidad_total,
                    'monto_total': venta.total,
                    'metodo_pago': venta.metodo_pago,
                    'creado_en': venta.creado_en,
                    'estado': venta.estado,
                    'detalles': detalles_list,
                })
        except Usuario.DoesNotExist:
            pass

    return render(request, 'core/inicio.html', {
        'historial_compras': historial_compras,
    })
