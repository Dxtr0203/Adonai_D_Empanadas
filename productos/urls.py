# productos/urls.py
from django.urls import path
from . import views

urlpatterns = [
   
    path("", views.catalogo, name="catalogo"),  # Aquí se usa la vista catalogo

    path("agregar-producto/", views.agregar_producto, name="agregar_producto"),
]
