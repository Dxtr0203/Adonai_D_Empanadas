# usuarios/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "usuarios"

urlpatterns = [
    # Ruta de login usando un template personalizado
    path("login/", auth_views.LoginView.as_view(template_name="usuarios/login.html"), name="login"),
    
    # Ruta de logout
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Ruta para el perfil del usuario
    path("perfil/", views.perfil, name="perfil"),
]
