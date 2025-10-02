from django.shortcuts import render, redirect
from .models import Producto, Categoria
from .forms import ProductoForm
from django.contrib import messages

def catalogo(request):
    productos = Producto.objects.all()
    categorias = Categoria.objects.all()
    return render(request, "productos/catalogo.html", {"productos": productos, "categorias": categorias})

# Vista para agregar un producto (solo administrador)
def agregar_producto(request):
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