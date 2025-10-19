# adonai/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),

    # Sitio público (inicio y catálogo)
    path('', include('core.urls')),  # Portada e información de la tienda

    # Catálogo público de productos
    path('catalogo/', include('productos.urls')),

    # Panel interno (inventario, administración)
    path('panel/', include('productos.panel_urls')),

    # Autenticación y gestión de usuarios (login, logout, etc.)
    path('usuarios/', include('usuarios.urls')),
    # Endpoints del chat (widget)
    path('chat/', include('chat.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
