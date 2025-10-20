from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User, Group
from .models import Usuario, Rol


class UsuarioBackend:
    """Autenticación contra la tabla legacy `usuarios`.

    Si las credenciales coinciden con un registro en `usuarios`, crea/actualiza
    un `auth.User` sincronizado (username=email.lower()) y lo devuelve.
    """

    def authenticate(self, request, username=None, password=None):
        if username is None or password is None:
            return None
        try:
            usuario = Usuario.objects.filter(email__iexact=username).first()
            if not usuario:
                return None

            # La contraseña en la tabla `usuarios` debería estar hasheada con los
            # mismos hasher de Django (si se creó con make_password). Usamos
            # check_password para validar.
            if not usuario.password:
                return None

            # Intentar verificación con hash Django
            if check_password(password, usuario.password):
                valid = True
            else:
                # Fallback: si la contraseña en la DB está en texto plano (legacy), comprobar y re-hashear
                if usuario.password == password:
                    valid = True
                    # re-hashear la contraseña usando el hasher de Django
                    from django.contrib.auth.hashers import make_password
                    usuario.password = make_password(password)
                    usuario.save(update_fields=['password'])
                else:
                    valid = False

            if not valid:
                return None

            # Obtener o crear el auth.User
            username_auth = usuario.email.lower()
            user, created = User.objects.get_or_create(username=username_auth, defaults={'email': usuario.email})

            # Sincronizar estado y password (guardamos el hash tal cual si ya es compatible)
            user.email = usuario.email
            # Si la contraseña en usuario ya está hasheada con formato Django, la copiamos.
            try:
                user.password = usuario.password
            except Exception:
                pass
            user.is_active = (usuario.estado == 'activo')
            user.save()

            # Asignar grupo según rol
            try:
                if usuario.rol and usuario.rol.nombre:
                    grupo, _ = Group.objects.get_or_create(name=usuario.rol.nombre)
                    user.groups.add(grupo)
            except Exception:
                pass

            return user
        except Exception:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
