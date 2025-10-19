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
from usuarios.models import Usuario, Rol
from usuarios.forms import UsuarioForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth.models import Group



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


@login_required
def empleado_list(request):
    # Permitir siempre a superusers; para otros, comprobar permiso y mostrar mensaje en UI
    if not (request.user.is_superuser or request.user.has_perm('usuarios.view_usuario')):
        messages.error(request, 'No tienes permiso para ver la lista de empleados.')
        return redirect('panel:dashboard')
    qs = Usuario.objects.filter(rol__nombre__in=['Empleado', 'Administrador']).order_by('-creado_en')
    return render(request, 'panel/empleado_list.html', {'empleados': qs})


@login_required
def empleado_create(request):
    # Comprobación explícita de permisos para dar feedback claro en UI
    if not request.user.has_perm('usuarios.add_usuario'):
        messages.error(request, 'No tienes permisos para crear empleados. Contacta al administrador.')
        return redirect('panel:dashboard')
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            try:
                usuario = form.save(commit=False)
                # Validar que no exista un Usuario con ese email
                if Usuario.objects.filter(email__iexact=usuario.email).exists():
                    form.add_error('email', 'Ya existe un usuario con este correo.')
                    messages.error(request, 'Ya existe un usuario con este correo.')
                    return render(request, 'panel/empleado_form.html', {'form': form, 'modo': 'Nuevo'})
                # Generar password aleatorio sencillo (se puede mejorar)
                import secrets
                raw_pw = secrets.token_urlsafe(8)
                # Generar un username único basado en el nombre
                base = ''.join(e for e in usuario.nombre.lower() if e.isalnum())
                if not base:
                    base = usuario.email.split('@')[0]
                username = base
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base}{counter}"
                    counter += 1

                # Crear auth.User con username generado y sin contraseña (se enviará link para crearla)
                auth_user = User.objects.create(username=username, email=usuario.email)
                auth_user.set_unusable_password()
                auth_user.save()

                # Asignar rol Empleado
                rol_emp, _ = Rol.objects.get_or_create(nombre='Empleado', defaults={'descripcion': 'Empleado del local'})
                usuario.rol = rol_emp
                # Forzar cambio de contraseña en el primer login
                usuario.must_change_password = True
                # Guardar contraseña hasheada en campo password
                from django.contrib.auth.hashers import make_password
                usuario.password = make_password(raw_pw)
                try:
                    usuario.save()
                except IntegrityError:
                    form.add_error('email', 'Ya existe un usuario con este correo.')
                    messages.error(request, 'Ya existe un usuario con este correo.')
                    return render(request, 'panel/empleado_form.html', {'form': form, 'modo': 'Nuevo'})

                # Asignar contraseña usable al auth_user y mostrar credenciales al admin (modo local)
                auth_user.set_password(raw_pw)
                auth_user.save()
                # Asegurar que el auth_user esté en el grupo Empleado
                try:
                    grupo_emp, _ = Group.objects.get_or_create(name='Empleado')
                    auth_user.groups.add(grupo_emp)
                except Exception:
                    pass
                messages.success(request, f'Empleado creado. Usuario: {username} | Contraseña: {raw_pw}')
                return redirect('panel:empleado_list')
            except Exception as e:
                # Mostrar el error en la UI para diagnóstico
                import traceback
                tb = traceback.format_exc()
                messages.error(request, f'Error al crear empleado: {e}')
                messages.error(request, f'Detalle: {tb.splitlines()[-1]}')
                return render(request, 'panel/empleado_form.html', {'form': form, 'modo': 'Nuevo'})
        messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = UsuarioForm()
    return render(request, 'panel/empleado_form.html', {'form': form, 'modo': 'Nuevo'})


@login_required
def empleado_update(request, pk):
    if not (request.user.is_superuser or request.user.has_perm('usuarios.change_usuario')):
        messages.error(request, 'No tienes permiso para editar empleados.')
        return redirect('panel:dashboard')
    empleado = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=empleado)
        if form.is_valid():
            usuario = form.save(commit=False)
            # Si cambió el email, verificar no colisionar con otro Usuario
            if Usuario.objects.filter(email__iexact=usuario.email).exclude(pk=empleado.pk).exists():
                form.add_error('email', 'Otro usuario ya usa este correo.')
                messages.error(request, 'Otro usuario ya usa este correo.')
                return render(request, 'panel/empleado_form.html', {'form': form, 'modo': 'Editar'})
            # Sincronizar email en auth.User
            username = usuario.email.lower()
            auth_user, created = User.objects.get_or_create(username=username, defaults={'email': usuario.email})
            if auth_user.email != usuario.email:
                auth_user.email = usuario.email
                auth_user.save()
            # Si el admin está editando el empleado, asumimos que ya pasó el primer acceso
            usuario.must_change_password = False
            usuario.save()
            # Asegurar que el auth_user esté en el grupo Empleado
            try:
                grupo_emp, _ = Group.objects.get_or_create(name='Empleado')
                auth_user.groups.add(grupo_emp)
            except Exception:
                pass
            messages.success(request, 'Empleado actualizado.')
            return redirect('panel:empleado_list')
        messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = UsuarioForm(instance=empleado)
    return render(request, 'panel/empleado_form.html', {'form': form, 'modo': 'Editar'})


@login_required
def empleado_delete(request, pk):
    if not (request.user.is_superuser or request.user.has_perm('usuarios.delete_usuario')):
        messages.error(request, 'No tienes permiso para eliminar empleados.')
        return redirect('panel:dashboard')
    empleado = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        nombre = empleado.nombre
        # Eliminar auth.User asociado si existe
        try:
            auth = User.objects.filter(username=empleado.email.lower()).first()
            if auth:
                auth.delete()
        except Exception:
            pass
        empleado.delete()
        messages.success(request, f'Empleado «{nombre}» eliminado.')
        return redirect('panel:empleado_list')
    return render(request, 'panel/confirm_delete.html', {'obj': empleado, 'tipo': 'Empleado'})
