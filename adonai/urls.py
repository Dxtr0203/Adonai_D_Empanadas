from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Panel de administración de Django
    path("admin/", admin.site.urls),

    # Sitio público (inicio y catálogo)
    path("", include("core.urls")),             # Portada e info de la tienda
    path("catalogo/", include("productos.urls")),  # Catálogo público

    # Panel interno (inventario, administración)
    path("panel/", include("productos.panel_urls")),

    # Autenticación y gestión de usuarios
    path("accounts/", include("usuarios.urls")),
]

# En desarrollo, servir archivos de media y estáticos
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
