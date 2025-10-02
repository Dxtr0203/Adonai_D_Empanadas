# usuarios/management/commands/bootstrap_roles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from productos.models import Producto, Categoria  # ajusta si tus modelos cambian

class Command(BaseCommand):
    help = "Crea grupos (Admin, Empleado, Cliente) y asigna permisos."

    def handle(self, *args, **kwargs):
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        empleado_group, _ = Group.objects.get_or_create(name="Empleado")
        cliente_group, _ = Group.objects.get_or_create(name="Cliente")

        producto_ct = ContentType.objects.get_for_model(Producto)
        categoria_ct = ContentType.objects.get_for_model(Categoria)

        # Permisos CRUD de productos
        perms_prod = Permission.objects.filter(content_type=producto_ct)
        perms_cat = Permission.objects.filter(content_type=categoria_ct)

        # Admin = todos
        admin_group.permissions.set(list(perms_prod) + list(perms_cat))

        # Empleado = ver, añadir, cambiar (no borrar)
        keep_codenames = {"view_producto", "add_producto", "change_producto",
                          "view_categoria"}
        empleado_group.permissions.set(
            [p for p in list(perms_prod) + list(perms_cat) if p.codename in keep_codenames]
        )

        # Cliente = sin permisos de modelo (navega la tienda)
        cliente_group.permissions.clear()

        self.stdout.write(self.style.SUCCESS("Roles y permisos configurados."))
