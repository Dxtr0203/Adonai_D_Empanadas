# usuarios/middleware.py
from django.utils.timezone import now
from django.conf import settings
from django.shortcuts import redirect

class LoginAttemptsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar si el usuario ya está autenticado
        if request.user.is_authenticated:
            return self.get_response(request)

        # Obtener intentos fallidos y hora del último intento fallido
        failed_attempts = request.session.get('failed_attempts', 0)
        last_failed_time = request.session.get('last_failed_time', None)

        # Si se superó el número de intentos fallidos, bloquea el acceso temporalmente
        if failed_attempts >= settings.LOGIN_FAILURE_LIMIT:
            time_since_last_attempt = now() - last_failed_time
            if time_since_last_attempt.seconds < settings.LOGIN_BLOCK_TIME:
                # Bloquea al usuario por 30 segundos
                return redirect('usuarios:login')  # Redirige al login con bloqueo

        # Incrementar los intentos fallidos si el intento es fallido
        if request.method == 'POST' and 'username' in request.POST:
            request.session['failed_attempts'] = failed_attempts + 1
            request.session['last_failed_time'] = now()

        response = self.get_response(request)
        return response
