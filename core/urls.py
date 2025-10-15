# core/urls.py
from django.urls import path
from . import views  # Importa las vistas de core

urlpatterns = [
    path('', views.inicio, name='inicio'),  # Ruta para la vista 'inicio'
]
