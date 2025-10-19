from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views

app_name = "usuarios"

urlpatterns = [
    # Ruta de login usando la vista personalizada (para soportar must_change_password)
    path("login/", views.custom_login, name="login"),
    
    # Ruta de logout
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Ruta para el perfil del usuario
    path("perfil/", views.perfil, name="perfil"),

    # Ruta para registro de nuevos usuarios
    path("register/", views.register, name="register"),

    # Ruta para forzar el cambio de contraseña
    path('force-password-change/', views.ForcePasswordChangeView.as_view(), name='force_password_change'),

    # Rutas de restablecimiento de contraseña (flujo de email)
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    
    # Ruta para la confirmación de reset de contraseña
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 
            auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
            name='password_reset_confirm'),
    
    # Ruta para confirmar la finalización del reset de contraseña
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]
