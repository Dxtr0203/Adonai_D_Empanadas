# usuarios/middleware.py
from django.utils.timezone import now
from django.conf import settings
from django.shortcuts import redirect
from datetime import datetime
 
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
        if failed_attempts >= getattr(settings, 'LOGIN_FAILURE_LIMIT', 5):
            if last_failed_time:
                # Convertir last_failed_time a datetime si es str
                if isinstance(last_failed_time, str):
                    try:
                        last_failed_time = datetime.fromisoformat(last_failed_time)
                    except Exception:
                        last_failed_time = None
                if last_failed_time:
                    time_since_last_attempt = now() - last_failed_time
                    if time_since_last_attempt.total_seconds() < getattr(settings, 'LOGIN_BLOCK_TIME', 30):
                        return redirect('usuarios:login')  # Redirige al login con bloqueo
 
        # Incrementar los intentos fallidos si el intento es fallido
        if request.method == 'POST' and 'username' in request.POST:
            request.session['failed_attempts'] = failed_attempts + 1
            request.session['last_failed_time'] = now().isoformat()
 
        response = self.get_response(request)
        return response