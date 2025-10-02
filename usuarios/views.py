from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from .forms import LoginForm
from .models import Usuario

# Mapear nombres de rol (Rol.nombre) a nombres de URL en tu proyecto
ROLE_REDIRECTS = {
    'Administrador': 'admin_dashboard',
    'Empleado': 'empleado_dashboard',
    'Cliente': 'cliente_home',
}

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = Usuario.objects.select_related('rol').get(email__iexact=email, estado='activo')
            except Usuario.DoesNotExist:
                messages.error(request, 'Email o contraseña incorrectos.')
                return render(request, 'usuarios/login.html', {'form': form})

            if check_password(password, user.password):
                # Guardar en sesión
                request.session['usuario_id'] = user.id
                request.session['usuario_nombre'] = user.nombre
                request.session['usuario_rol'] = user.rol.nombre if user.rol else ''
                # Opcional: expirar al cerrar navegador
                request.session.set_expiry(0)
                # Redirigir por rol
                redirect_name = ROLE_REDIRECTS.get(user.rol.nombre, 'home')
                return redirect(reverse(redirect_name))
            else:
                messages.error(request, 'Email o contraseña incorrectos.')
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})

def logout_view(request):
    # Borrar sesión segura
    request.session.flush()
    return redirect('usuarios:login')