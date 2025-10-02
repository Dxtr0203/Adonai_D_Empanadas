from django.shortcuts import render
from .models import Usuario

def perfil(request):
    usuario = request.user
    return render(request, 'usuarios/perfil.html', {'usuario': usuario})
