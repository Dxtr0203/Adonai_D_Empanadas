from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Ruta para el panel de administración de Django
    path("admin/", admin.site.urls),

    # Sitio público (catálogo de productos)
    path("", include("productos.urls")),  # Incluye las URLs de la aplicación 'productos' para el catálogo público

    # Panel interno (administración de inventario)
    path("panel/", include("productos.panel_urls")),  # Incluye las URLs para el panel de administración de inventarios y otras configuraciones internas

    # Rutas de autenticación y gestión de usuarios
    path("accounts/", include("usuarios.urls")),  # Incluye las URLs de la aplicación 'usuarios' para autenticación y gestión de usuarios
]

# Si estamos en modo DEBUG, servir archivos estáticos y de medios
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
