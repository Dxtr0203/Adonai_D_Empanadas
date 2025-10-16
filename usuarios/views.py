from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.utils.timezone import now
from django.conf import settings
from django.contrib.auth.models import User  # Importando el modelo User
from .forms import UsuarioForm, RegistroFormulario  # Importa los formularios

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
            if last_failed_time:  # Asegura que last_failed_time no sea None
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
        
        # Incrementa los intentos fallidos y guarda el tiempo
        request.session['failed_attempts'] = failed_attempts + 1
        request.session['last_failed_time'] = now().strftime('%Y-%m-%d %H:%M:%S')  # Convierte datetime a string

    return render(request, 'usuarios/login.html')  # Vuelve a mostrar el formulario de login


# Vista para el perfil del usuario (requiere autenticación)
@login_required
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


# Vista para el registro de nuevos usuarios
def registro(request):
    if request.method == 'POST':
        form = RegistroFormulario(request.POST)
        if form.is_valid():
            # Aquí debemos asegurarnos de que se cree el usuario correctamente
            user = form.save(commit=False)  # No lo guardamos aún, para poder manejar la contraseña
            user.set_password(form.cleaned_data['password1'])  # Establece la contraseña de forma segura
            user.save()  # Guarda el usuario en la base de datos
            login(request, user)  # Inicia sesión automáticamente
            messages.success(request, "¡Registro exitoso! Ahora puedes iniciar sesión.")
            return redirect('inicio')  # Redirige al inicio después del registro
    else:
        form = RegistroFormulario()

    return render(request, 'usuarios/registro.html', {'form': form})  # Muestra el formulario de registro
