# core/views.py
from django.shortcuts import render, redirect
from pagos.models import Payment


def inicio(request):
    """Página de inicio pública para clientes.

    Ahora pública: no redirige al login automáticamente. Si el usuario está
    autenticado verá el menú de usuario en el header; si no, verá el botón
    "Registrarse".
    """
    historial_compras = []
    if request.user.is_authenticated:
        historial_compras = Payment.objects.filter(status__in=['paid', 'created']).order_by('-created_at')

    return render(request, 'core/inicio.html', {
        'historial_compras': historial_compras,
    })
