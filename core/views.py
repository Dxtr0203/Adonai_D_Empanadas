# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required  # Asegura que solo los usuarios autenticados puedan acceder
def inicio(request):
    return render(request, 'core/inicio.html')
