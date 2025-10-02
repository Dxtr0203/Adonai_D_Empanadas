# usuarios/middleware.py
from .models import Usuario

class LoadUsuarioMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.usuario = None
        usuario_id = request.session.get('usuario_id')
        if usuario_id:
            try:
                request.usuario = Usuario.objects.select_related('rol').get(pk=usuario_id)
            except Usuario.DoesNotExist:
                request.usuario = None
        return self.get_response(request)
