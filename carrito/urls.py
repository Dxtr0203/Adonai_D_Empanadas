from django.urls import path
from . import views

app_name = 'carrito'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
]
