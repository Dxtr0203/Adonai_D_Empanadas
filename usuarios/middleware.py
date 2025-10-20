from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.conf import settings
from django.shortcuts import redirect


class LoginAttemptsMiddleware:
        def __init__(self, get_response):
                self.get_response = get_response

        def __call__(self, request):
                # Allow unauthenticated access to auth-related paths (login, logout, password reset)
                login_path = getattr(settings, 'LOGIN_URL', '/usuarios/login/') or '/usuarios/login/'
                if request.path.startswith(login_path) or request.path.startswith('/usuarios/'):
                        return self.get_response(request)

                # If the user is authenticated, reset counters and continue
                if request.user.is_authenticated:
                        request.session['failed_attempts'] = 0
                        request.session['last_failed_time'] = None
                        return self.get_response(request)

                failed_attempts = request.session.get('failed_attempts', 0)
                last_failed_time_raw = request.session.get('last_failed_time', None)

                last_failed_time = None
                if isinstance(last_failed_time_raw, str):
                        last_failed_time = parse_datetime(last_failed_time_raw)
                        if last_failed_time is not None and timezone.is_naive(last_failed_time):
                                last_failed_time = timezone.make_aware(last_failed_time, timezone.get_current_timezone())
                else:
                        last_failed_time = last_failed_time_raw

                # If attempts exceeded and still in block window, redirect to login (auth routes are excluded above)
                if failed_attempts >= getattr(settings, 'LOGIN_FAILURE_LIMIT', 3) and last_failed_time is not None:
                        time_since_last_attempt = timezone.now() - last_failed_time
                        if time_since_last_attempt.total_seconds() < getattr(settings, 'LOGIN_BLOCK_TIME', 30):
                                return redirect(settings.LOGIN_URL)

                # Only increment on POST when authentication actually fails
                if request.method == 'POST' and 'username' in request.POST:
                        username = request.POST.get('username')
                        password = request.POST.get('password')
                        if username and password and not request.user.is_authenticated:
                                from django.contrib.auth import authenticate
                                user = authenticate(request, username=username, password=password)
                                # Don't count attempts for superusers
                                if user is not None and user.is_superuser:
                                        return self.get_response(request)
                                if user is None:
                                        request.session['failed_attempts'] = failed_attempts + 1
                                        request.session['last_failed_time'] = timezone.now().isoformat()

                response = self.get_response(request)
                return response
