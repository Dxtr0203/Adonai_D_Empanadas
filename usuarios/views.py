from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages  # Para manejar los mensajes de éxito/error
from django.utils.timezone import now  # Para manejar los tiempos
from django.conf import settings
from .models import Usuario
from .forms import UsuarioForm  # Importa el formulario que vamos a utilizar para editar el perfil

# Vista personalizada de login
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Verifica los intentos fallidos
        failed_attempts = request.session.get('failed_attempts', 0)
        last_failed_time = request.session.get('last_failed_time', None)

        # Si el número de intentos fallidos es mayor o igual al límite configurado, aplica el bloqueo
        if failed_attempts >= settings.LOGIN_FAILURE_LIMIT:
            time_since_last_attempt = now() - last_failed_time
            if time_since_last_attempt.seconds < settings.LOGIN_BLOCK_TIME:
                # Bloquea el acceso durante 30 segundos después de 3 intentos fallidos
                messages.error(request, f"Has superado el número máximo de intentos. Intenta nuevamente en {settings.LOGIN_BLOCK_TIME} segundos.")
                return redirect('usuarios:login')  # Redirige al login para intentar nuevamente después del bloqueo

        # Autentica al usuario
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Inicia sesión si las credenciales son correctas
            return redirect('usuarios:perfil')  # Redirige al perfil

        # Si el usuario no es válido, muestra el mensaje de error
        messages.error(request, "Credenciales incorrectas. Por favor, verifica tu usuario y contraseña.")
        
        # Incrementa los intentos fallidos
        request.session['failed_attempts'] = failed_attempts + 1
        request.session['last_failed_time'] = now()  # Actualiza el tiempo del último intento fallido

    return render(request, 'usuarios/login.html')  # Vuelve a mostrar el formulario de login


@login_required  # Asegura que solo los usuarios autenticados puedan acceder
def perfil(request):
    usuario = request.user  # Obtiene el usuario autenticado

    # Si se recibe un POST (al editar el perfil), procesamos los datos del formulario
    if request.method == "POST":
        form = UsuarioForm(request.POST, instance=usuario)  # Rellena el formulario con los datos del usuario
        if form.is_valid():  # Verifica si el formulario es válido
            form.save()  # Guarda los cambios en el perfil
            messages.success(request, "¡Perfil actualizado correctamente!")  # Mensaje de éxito
            return redirect('usuarios:perfil')  # Redirige al perfil después de guardar los cambios
        else:
            messages.error(request, "Hubo un error al actualizar el perfil. Por favor, revisa los campos.")  # Mensaje de error
    else:
        form = UsuarioForm(instance=usuario)  # Si es GET, mostramos el formulario con los datos actuales del usuario

    return render(request, 'usuarios/perfil.html', {'usuario': usuario, 'form': form})  # Muestra el perfil y el formulario
