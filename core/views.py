# core/views.py
from django.shortcuts import render, redirect


def inicio(request):
    """Página de inicio pública para clientes.

    Ahora pública: no redirige al login automáticamente. Si el usuario está
    autenticado verá el menú de usuario en el header; si no, verá el botón
    "Registrarse".
    """
    return render(request, 'core/inicio.html')
