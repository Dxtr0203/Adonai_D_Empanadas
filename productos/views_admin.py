# productos/views_admin.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, F

from .models import Producto, Categoria
from .forms import ProductoForm, CategoriaForm
from usuarios.decorators import group_required
# productos/views_admin.py
from .forms import ProductoForm, CategoriaForm



# --------- Dashboard ---------
@login_required
@group_required("Admin", "Empleado")
def dashboard(request):
    # Productos con stock igual o por debajo del mínimo
    low_stock = Producto.objects.filter(stock_actual__lte=F("stock_minimo")).select_related("categoria")
    total_prod = Producto.objects.count()
    return render(request, "panel/dashboard.html", {
        "total_prod": total_prod,
        "low_stock": low_stock[:8],
    })


# --------- Inventario / Productos ---------
@login_required
@group_required("Admin", "Empleado")
def inventario_list(request):
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("categoria", "").strip()

    qs = (Producto.objects
          .select_related("categoria")
          .order_by("-id"))

    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    if cat:
        qs = qs.filter(categoria_id=cat)

    categorias = Categoria.objects.all().order_by("nombre")
    return render(request, "panel/inventario_list.html", {
        "productos": qs,
        "categorias": categorias,
        "q": q,
        "categoria_sel": cat
    })


@login_required
@permission_required("productos.add_producto", raise_exception=True)
def producto_create(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            p = form.save()
            messages.success(request, f"Producto «{p.nombre}» creado.")
            return redirect("panel:inventario_list")
        messages.error(request, "Revisa los errores del formulario.")
    else:
        form = ProductoForm()
    return render(request, "panel/producto_form.html", {"form": form, "modo": "Crear"})


@login_required
@permission_required("productos.change_producto", raise_exception=True)
def producto_update(request, pk):
    p = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=p)
        if form.is_valid():
            form.save()
            messages.success(request, f"Producto «{p.nombre}» actualizado.")
            return redirect("panel:inventario_list")
        messages.error(request, "Revisa los errores del formulario.")
    else:
        form = ProductoForm(instance=p)
    return render(request, "panel/producto_form.html", {"form": form, "modo": "Editar"})


@login_required
@permission_required("productos.delete_producto", raise_exception=True)
def producto_delete(request, pk):
    p = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        nombre = p.nombre
        p.delete()
        messages.success(request, f"Producto «{nombre}» eliminado.")
        return redirect("panel:inventario_list")
    return render(request, "panel/confirm_delete.html", {"obj": p, "tipo": "Producto"})


# --------- Categorías ---------
@login_required
@permission_required("productos.view_categoria", raise_exception=True)
def categoria_list(request):
    categorias = Categoria.objects.all().order_by("nombre")
    return render(request, "panel/categoria_list.html", {"categorias": categorias})


@login_required
@permission_required("productos.add_categoria", raise_exception=True)
def categoria_create(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            c = form.save()
            messages.success(request, f"Categoría «{c.nombre}» creada.")
            return redirect("panel:categoria_list")
        messages.error(request, "Corrige los errores del formulario.")
    else:
        form = CategoriaForm()
    return render(request, "panel/categoria_form.html", {"form": form, "modo": "Nueva"})


@login_required
@permission_required("productos.change_categoria", raise_exception=True)
def categoria_update(request, pk):
    c = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":
        form = CategoriaForm(request.POST, instance=c)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría actualizada.")
            return redirect("panel:categoria_list")
        messages.error(request, "Corrige los errores del formulario.")
    else:
        form = CategoriaForm(instance=c)
    return render(request, "panel/categoria_form.html", {"form": form, "modo": "Editar"})


@login_required
@permission_required("productos.delete_categoria", raise_exception=True)
def categoria_delete(request, pk):
    c = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":
        nombre = c.nombre
        c.delete()
        messages.success(request, f"Categoría «{nombre}» eliminada.")
        return redirect("panel:categoria_list")
    return render(request, "panel/confirm_delete.html", {"obj": c, "tipo": "Categoría"})
