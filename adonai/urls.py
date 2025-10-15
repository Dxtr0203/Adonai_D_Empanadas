from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),

    # Sitio público (inicio y catálogo)
    path('', include('core.urls')),  # Portada e información de la tienda
    # Asegúrate de que esta ruta esté definida correctamente en `core/urls.py` para el inicio

    # Catálogo público de productos
    path('catalogo/', include('productos.urls')),  # Catálogo público de productos

    # Panel interno (inventario, administración)
    path('panel/', include('productos.panel_urls')),  # Aquí se redirige al panel de administración

    # Autenticación y gestión de usuarios (login, logout, etc.)
    path('usuarios/', include('usuarios.urls')),  # Aquí se maneja el login, logout, y perfil de usuario

    # Si es necesario, se pueden agregar más rutas de administración aquí
]

# En desarrollo, servir archivos de media y estáticos
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
