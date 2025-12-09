from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views

app_name = "usuarios"

urlpatterns = [
    # Ruta de login usando la vista personalizada (para soportar must_change_password)
    path("login/", views.custom_login, name="login"),
    
    # Ruta de logout personalizado (cierra sesión y redirige a inicio)
    path("logout/", views.custom_logout, name="logout"),

    # Ruta para el perfil del usuario
    path("perfil/", views.perfil, name="perfil"),

    # Ruta para cambiar contraseña desde el perfil (cliente)
    path("cambiar-contrasena/", views.cambiar_contrasena_cliente, name="cambiar_contrasena"),

    # Ruta para registro de nuevos usuarios
    path("register/", views.register, name="register"),

    # Ruta para forzar el cambio de contraseña
   path('force-password-change/', views.force_password_change, name='force_password_change'),

    # Rutas de recuperación de contraseña (modal)
    path('recovery/verify/', views.recovery_verify, name='recovery_verify'),
    path('recovery/verify-code/', views.recovery_verify_code, name='recovery_verify_code'),
    path('recovery/verify-code-only/', views.recovery_verify_code_only, name='recovery_verify_code_only'),

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
