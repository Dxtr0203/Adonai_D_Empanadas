# usuarios/decorators.py
from functools import wraps
from django.shortcuts import redirect

def usuario_login_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            return redirect('usuarios:login')
        return view_func(request, *args, **kwargs)
    return _wrapped

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            rol = request.session.get('usuario_rol')
            if not rol or (rol not in allowed_roles):
                return redirect('usuarios:login')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
