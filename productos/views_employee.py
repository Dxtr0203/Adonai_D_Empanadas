from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import F
from usuarios.decorators import group_required
from .models import Producto


@login_required
@group_required('Empleado')
def empleado_dashboard(request):
    # Información resumida para el empleado
    total_productos = Producto.objects.count()
    low_stock = Producto.objects.filter(stock_actual__lte=F('stock_minimo'))[:5]
    return render(request, 'panel/empleado_dashboard.html', {'total_productos': total_productos, 'low_stock': low_stock})


@login_required
@group_required('Empleado')
def empleado_inventario(request):
    # Lista de productos en modo solo lectura
    productos = Producto.objects.select_related('categoria').order_by('-id')
    return render(request, 'panel/empleado_inventario.html', {'productos': productos})


@login_required
@group_required('Empleado')
def empleado_perfil(request):
    return render(request, 'panel/empleado_perfil.html')
