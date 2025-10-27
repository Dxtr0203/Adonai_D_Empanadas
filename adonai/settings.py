from pathlib import Path
import os

# === Paths ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === Seguridad / Debug (solo dev) ===
SECRET_KEY = 'django-insecure-kfxcl-@8q4l=r8!c-)rb20w+cp&&8m&suw-$c^1=^fo+ar47)-'
DEBUG = True  # Cambiar a False en producción
# En desarrollo permitir hosts locales y 'testserver' para las pruebas con Client()
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'testserver']  # Aquí puedes agregar los dominios permitidos cuando esté en producción

# === Apps ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # Utilidades para formatear números/precios

    # Apps personalizadas del proyecto
    'usuarios',
    'productos.apps.ProductosConfig',
    'ventas',
    'carrito',
    'delivery',
    'chat',
    'core',
    'roles',  # Agregar la app de roles
    'django.contrib.sites',
]

# === Middleware ===
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'usuarios.middleware.LoginAttemptsMiddleware',  # Agregar el middleware personalizado para bloqueo de intentos
]

ROOT_URLCONF = 'adonai.urls'

# === Templates ===
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',              # Carpeta global para templates
            BASE_DIR / 'adonai' / 'templates',   # Plantillas dentro del proyecto (si las tienes)
        ],
        'APP_DIRS': True,  # Permite buscar templates dentro de cada app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'adonai.wsgi.application'

# === Base de datos ===
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'adonai_store',  # Nombre de la base de datos
        'USER': 'root',  # Usuario para la base de datos
        'PASSWORD': 'dexter123',  # Contraseña de la base de datos
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# === Validación de contraseñas ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# === Internacionalización ===
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/La_Paz'
USE_I18N = True
USE_TZ = True

# === Archivos estáticos (CSS/JS/imagenes del front) ===
STATIC_URL = "/static/"

# Carpeta de archivos estáticos para desarrollo (archivos que TÚ pones en /static)
STATICFILES_DIRS = [
    BASE_DIR / "static",   # Ruta para archivos estáticos adicionales
]

# Carpeta destino para collectstatic (producción)
STATIC_ROOT = BASE_DIR / "staticfiles"

# === Archivos de media (subidos por usuarios) ===
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"     # Ruta para los archivos subidos por usuarios

# === Autenticación y login multi-rol ===
LOGIN_URL = '/usuarios/login/'  # Ruta para acceder al login
LOGIN_REDIRECT_URL = "/panel/"  # Redirigir después de login, a la página principal del panel (ajustado para tu panel personalizado)
LOGOUT_REDIRECT_URL = "/"  # Redirigir después de logout a la página de inicio

# === Configuración de Autenticación ===
AUTHENTICATION_BACKENDS = [
    'usuarios.backends.UsuarioBackend',
    'django.contrib.auth.backends.ModelBackend',  # Autenticación por defecto
]

# --- Configuración adicional de seguridad ---
SECURE_SSL_REDIRECT = False  # En desarrollo, debe estar en False. En producción, ponlo en True si usas HTTPS
CSRF_COOKIE_SECURE = False  # En desarrollo, debe estar en False. En producción, ponlo en True si usas HTTPS
SESSION_COOKIE_SECURE = False  # En desarrollo, debe estar en False. En producción, ponlo en True si usas HTTPS

# --- Bloqueo de intentos fallidos (opcional) --- 
# Implementar un bloqueo de 30 segundos después de 3 intentos fallidos
LOGIN_FAILURE_LIMIT = 3  # Número de intentos fallidos
LOGIN_BLOCK_TIME = 30  # Tiempo de bloqueo en segundos

# --- Otras configuraciones ---
SESSION_COOKIE_AGE = 86400  # La sesión expirará después de 24 horas (en segundos)

# Expirar la sesión al cerrar el navegador (útil en desarrollo para no mantener login persistente)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# === Email (configurable por variables de entorno) ===
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'no-reply@adonai.local')

# Sites framework (necesario para construir enlaces con dominio)
SITE_ID = int(os.environ.get('SITE_ID', 1))
