from django.shortcuts import render, redirect
from .models import Producto, Categoria
from .forms import ProductoForm
from django.contrib import messages
from django.db.models import Q

def catalogo(request):
    """
    Vista del catálogo de productos con filtros por categoría y precio.
    """
    # Obtener todas las categorías para mostrar en el filtro
    categorias = Categoria.objects.all()

    # Obtener todos los productos
    productos = Producto.objects.all()

    # Filtrar por categoría si se pasa en GET
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    # Filtrar por rango de precio si se pasa en GET
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    if precio_min and precio_max:
        try:
            productos = productos.filter(precio__gte=float(precio_min), precio__lte=float(precio_max))
        except ValueError:
            messages.error(request, "El rango de precios no es válido.")

    return render(request, "productos/catalogo.html", {
        "productos": productos,
        "categorias": categorias,
        "categoria_id": categoria_id,
        "precio_min": precio_min,
        "precio_max": precio_max,
    })


def agregar_producto(request):
    """
    Vista para agregar un producto (solo administradores).
    """
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f"✅ '{producto.nombre}' agregado correctamente.")
            return redirect("catalogo")
        else:
            messages.error(request, "Revisa los campos marcados en rojo.")
    else:
        form = ProductoForm()

    return render(request, "productos/agregar_producto.html", {"form": form})
