from django.urls import path
from . import views

urlpatterns = [
    path("", views.catalogo, name="catalogo"),  # Aquí se usa la vista catalogo
    path("agregar-producto/", views.agregar_producto, name="agregar_producto"),  # Aquí se configura la URL para agregar productos
    path("ultimos/", views.ultimos_productos, name="ultimos_productos"),
    path("notificaciones/", views.notifications_unread, name="notifications_unread"),
    path("notificaciones/marcar/", views.mark_notification_read, name="mark_notification_read"),
]
