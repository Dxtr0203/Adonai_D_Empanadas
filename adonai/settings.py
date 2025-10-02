"""
Django settings for adonai project.
"""

from pathlib import Path
import os

# === Paths ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === Seguridad / Debug (solo dev) ===
SECRET_KEY = 'django-insecure-kfxcl-@8q4l=r8!c-)rb20w+cp&&8m&suw-$c^1=^fo+ar47)-'
DEBUG = True
ALLOWED_HOSTS = []

# === Apps ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Utilidades
    'django.contrib.humanize',  # formateo de números/precios en templates

    # Apps del proyecto
    'usuarios',
    'productos.apps.ProductosConfig',
    'ventas',
    'carrito',
    'delivery',
    'chat',
    'core',
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
]

ROOT_URLCONF = 'adonai.urls'

# === Templates ===
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',              # /templates/base.html, etc.
            BASE_DIR / 'adonai' / 'templates',   # si mantienes templates dentro del proyecto
        ],
        'APP_DIRS': True,  # también busca en app/templates/
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
        'NAME': 'adonai_store',
        'USER': 'root',
        'PASSWORD': '123456',
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

# Carpeta de estáticos para desarrollo (archivos que TÚ pones en /static)
STATICFILES_DIRS = [
    BASE_DIR / "static",   # ej: /static/img/hero-pets.jpg
]

# Carpeta destino para collectstatic (producción)
STATIC_ROOT = BASE_DIR / "staticfiles"

# === Archivos de media (subidos por usuarios) ===
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"     # ej: /media/productos/imagen.jpg

# === Autenticación y login multi-rol ===
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/panel/"
LOGOUT_REDIRECT_URL = "/"

# === Clave primaria por defecto ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
