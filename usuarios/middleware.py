from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.conf import settings
from django.shortcuts import redirect
from datetime import datetime
 
class LoginAttemptsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
 
    def __call__(self, request):
        # Verificar si el usuario ya está autenticado
        if request.user.is_authenticated:
            # Si el usuario está autenticado, restablecer los intentos fallidos
            request.session['failed_attempts'] = 0
            request.session['last_failed_time'] = None
            return self.get_response(request)

        # Obtener intentos fallidos y hora del último intento fallido (guardada como ISO string)
        failed_attempts = request.session.get('failed_attempts', 0)
        last_failed_time_raw = request.session.get('last_failed_time', None)

        # Parsear la hora si viene como string (ISO), y asegurarnos que sea timezone-aware
        last_failed_time = None
        if isinstance(last_failed_time_raw, str):
            last_failed_time = parse_datetime(last_failed_time_raw)
            if last_failed_time is not None and timezone.is_naive(last_failed_time):
                last_failed_time = timezone.make_aware(last_failed_time, timezone.get_current_timezone())
        else:
            last_failed_time = last_failed_time_raw

        # Si se superó el número de intentos fallidos, bloquea el acceso temporalmente
        if failed_attempts >= settings.LOGIN_FAILURE_LIMIT and last_failed_time is not None:
            time_since_last_attempt = timezone.now() - last_failed_time
            if time_since_last_attempt.total_seconds() < settings.LOGIN_BLOCK_TIME:
                # Bloquea al usuario por el tiempo configurado
                return redirect('usuarios:login')  # Redirige al login con bloqueo

        # Solo incrementar los intentos fallidos si el intento de login es fallido
        if request.method == 'POST' and 'username' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            # Si el usuario es superusuario, no incrementamos los intentos fallidos
            if username and password and not request.user.is_authenticated:
                from django.contrib.auth import authenticate
                user = authenticate(request, username=username, password=password)
                if user is not None and user.is_superuser:
                    # Si es superusuario, no incrementar intentos fallidos
                    return self.get_response(request)

                # Incrementar los intentos fallidos solo si el login es incorrecto
                request.session['failed_attempts'] = failed_attempts + 1
                # Guardar la fecha/hora como string ISO para que sea serializable por JSON
                request.session['last_failed_time'] = timezone.now().isoformat()

        response = self.get_response(request)
        return response