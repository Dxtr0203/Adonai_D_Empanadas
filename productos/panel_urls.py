# productos/panel_urls.py
from django.urls import path
from . import views_admin as views
from . import views_employee as views_emp

app_name = "panel"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    # Inventario
    path("inventario/", views.inventario_list, name="inventario_list"),
    path("inventario/nuevo/", views.producto_create, name="producto_create"),
    path("inventario/<int:pk>/editar/", views.producto_update, name="producto_update"),
    path("inventario/<int:pk>/eliminar/", views.producto_delete, name="producto_delete"),

    # Categorías
    path("categorias/", views.categoria_list, name="categoria_list"),
    path("categorias/nueva/", views.categoria_create, name="categoria_create"),
    path("categorias/<int:pk>/editar/", views.categoria_update, name="categoria_update"),
    path("categorias/<int:pk>/eliminar/", views.categoria_delete, name="categoria_delete"),
    # Empleados
    path("empleados/", views.empleado_list, name="empleado_list"),
    path("empleados/nuevo/", views.empleado_create, name="empleado_create"),
    path("empleados/<int:pk>/editar/", views.empleado_update, name="empleado_update"),
    path("empleados/<int:pk>/eliminar/", views.empleado_delete, name="empleado_delete"),
    # Area para empleados (limitada)
    path("empleados/area/", views_emp.empleado_dashboard, name="empleado_area_dashboard"),
    path("empleados/area/inventario/", views_emp.empleado_inventario, name="empleado_area_inventario"),
    path("empleados/area/perfil/", views_emp.empleado_perfil, name="empleado_area_perfil"),
]
