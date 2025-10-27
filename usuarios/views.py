from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages  # Para manejar los mensajes de éxito/error
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.conf import settings
from .models import Usuario
from .forms import UsuarioForm  # Importa el formulario que vamos a utilizar para editar el perfil
from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import resolve_url

# Formulario simple para registro
class RegistroForm(forms.ModelForm):
    # Hacemos opcional la contraseña en el formulario: si no se proporciona,
    # asignaremos la contraseña por defecto 'clientes123'. Esto facilita el
    # registro desde el header u otros formularios simples.
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña", required=False)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña", required=False)

    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'password', 'password_confirm', 'telefono', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(+591) 7xx-xxxxxx'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección, ciudad, referencia'}),
        }

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        pw2 = cleaned.get('password_confirm')
        # Si no se proporcionó contraseña, asignar la por defecto
        if not pw and not pw2:
            cleaned['password'] = 'clientes123'
            cleaned['password_confirm'] = 'clientes123'
            pw = pw2 = 'clientes123'

        if pw and pw2 and pw != pw2:
            raise forms.ValidationError('Las contraseñas no coinciden')
        return cleaned


def register(request):
    """Vista para registrar nuevos clientes."""
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            raw_password = form.cleaned_data.get('password') or 'clientes123'
            email = form.cleaned_data['email']
            username_for_auth = email.lower()

            # Evitar duplicados: si ya existe un auth.User o un registro en usuarios
            if User.objects.filter(username=username_for_auth).exists() or Usuario.objects.filter(email__iexact=email).exists():
                form.add_error('email', 'Ya existe una cuenta con este correo. Por favor inicia sesión o recupera tu contraseña.')
            else:
                # Crear el usuario en la tabla legacy (Usuario) con password hasheada
                from .models import Rol
                rol_cliente, _created = Rol.objects.get_or_create(nombre='Cliente', defaults={'descripcion': 'Rol por defecto: Cliente'})
                usuario = form.save(commit=False)
                usuario.password = make_password(raw_password)
                usuario.rol = rol_cliente
                usuario.save()

                # Crear el auth.User sincronizado y marcar como activo
                user_auth = User.objects.create_user(username=username_for_auth, email=email, password=raw_password)
                user_auth.is_active = (usuario.estado == 'activo')
                user_auth.save()

                # Por seguridad/UX: no iniciar sesión automáticamente tras el registro.
                # Redirigir al formulario de login y mostrar un mensaje de éxito.
                messages.success(request, 'Cuenta creada correctamente. Por favor inicia sesión.')
                return redirect('usuarios:login')
    else:
        form = RegistroForm()

    return render(request, 'usuarios/register.html', {'form': form})

# Vista personalizada de login
def custom_login(request):
    # Verifica los intentos fallidos (inicializar siempre para evitar UnboundLocalError)
    failed_attempts = request.session.get('failed_attempts', 0)
    last_failed_time_raw = request.session.get('last_failed_time', None)
    # Solo procesar credenciales cuando es un POST: evita incrementar contadores en GET
    if request.method == 'POST':
        username = request.POST.get('username')  # Aquí debería ir el email si estás usando el email como username
        password = request.POST.get('password')

        # Parsear la hora si viene como string
        last_failed_time = None
        if isinstance(last_failed_time_raw, str):
            last_failed_time = parse_datetime(last_failed_time_raw)
            if last_failed_time is not None and timezone.is_naive(last_failed_time):
                last_failed_time = timezone.make_aware(last_failed_time, timezone.get_current_timezone())
        else:
            last_failed_time = last_failed_time_raw

        # Si el número de intentos fallidos es mayor o igual al límite configurado, aplica el bloqueo
        if failed_attempts >= settings.LOGIN_FAILURE_LIMIT and last_failed_time is not None:
            time_since_last_attempt = timezone.now() - last_failed_time
            if time_since_last_attempt.total_seconds() < settings.LOGIN_BLOCK_TIME:
                messages.error(request, f"Has superado el número máximo de intentos. Intenta nuevamente en {settings.LOGIN_BLOCK_TIME} segundos.")
                # Renderizar la plantilla de login en vez de redirigir para evitar posibles bucles
                return render(request, 'usuarios/login.html')

        # Autentica al usuario
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Inicia sesión si las credenciales son correctas
            # Resetear contadores de intentos al iniciar sesión correctamente
            request.session['failed_attempts'] = 0
            request.session['last_failed_time'] = None

            # Manejar redirección 'next' (si viene de login?next=/ruta)
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                # Validar que el next sea seguro
                if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    return redirect(next_url)

            # Si es superuser, redirigir al panel personalizado de la aplicación
            if user.is_superuser:
                return redirect('panel:dashboard')  # Redirige al dashboard de tu panel personalizado
            # Si pertenece al grupo Empleado, redirigir al panel de empleado limitado
            if user.groups.filter(name='Empleado').exists():
                # Si el empleado tiene marcado que debe cambiar contraseña, redirigir al cambio
                try:
                    usuario_custom = Usuario.objects.get(email__iexact=user.email)
                    if getattr(usuario_custom, 'must_change_password', False):
                        return redirect('usuarios:force_password_change')
                except Usuario.DoesNotExist:
                    pass
                return redirect('panel:empleado_area_dashboard')  # Redirige al dashboard del empleado
            # Para usuarios normales (clientes), redirigir a la página principal
            return redirect('inicio')  # Redirige a la página principal del cliente

        # Si el usuario no es válido, muestra el mensaje de error y contabiliza el intento
        messages.error(request, "Credenciales incorrectas. Por favor, verifica tu usuario y contraseña.")
        # Incrementa los intentos fallidos solo en POST fallidos
        request.session['failed_attempts'] = failed_attempts + 1
        request.session['last_failed_time'] = timezone.now().isoformat()

    return render(request, 'usuarios/login.html')  # Vuelve a mostrar el formulario de login


# Vista para el perfil del usuario (requiere autenticación)
@login_required
def perfil(request):
    # Permitir que el usuario edite su perfil desde esta vista.
    try:
        usuario = Usuario.objects.get(email__iexact=request.user.email)
    except Usuario.DoesNotExist:
        # Si no existe el registro legacy, intentamos usar el auth.User como fallback
        usuario = None

    if request.method == 'POST':
        # Si tenemos registro en Usuario, lo editamos; si no, intentamos guardar en auth.User (mínimo)
        if usuario:
            form = UsuarioForm(request.POST, instance=usuario)
        else:
            # Crear un pequeño objeto temporal para validar los campos
            form = UsuarioForm(request.POST)

        if form.is_valid():
            saved = form.save(commit=False)
            # Si existe el registro legacy, guardar y sincronizar con auth.User
            if usuario:
                saved.id = usuario.id
                saved.save()
            else:
                # No tenemos modelo Usuario: intenta crear uno asociado al email actual
                try:
                    saved.save()
                except Exception:
                    pass

            # Sincronizar el email en auth.User si es necesario
            try:
                from django.contrib.auth.models import User as AuthUser
                auth_user = AuthUser.objects.filter(email__iexact=request.user.email).first()
                if auth_user:
                    # Actualizar email si el formulario lo cambió
                    new_email = form.cleaned_data.get('email')
                    if new_email and new_email.lower() != auth_user.email.lower():
                        auth_user.email = new_email.lower()
                        auth_user.username = new_email.lower()
                        auth_user.save()
            except Exception:
                pass

            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('usuarios:perfil')
    else:
        if usuario:
            form = UsuarioForm(instance=usuario)
        else:
            # Rellenar campos mínimos desde auth.User
            initial = {}
            try:
                initial['email'] = request.user.email
                initial['nombre'] = getattr(request.user, 'first_name', '')
            except Exception:
                pass
            form = UsuarioForm(initial=initial)

    return render(request, 'usuarios/perfil.html', {'form': form, 'usuario_obj': usuario})


@method_decorator(login_required, name='dispatch')
class ForcePasswordChangeView(PasswordChangeView):
    # Default template and redirect for regular users
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('usuarios:perfil')

    def get_template_names(self):
        # Si el usuario es empleado, usar plantilla del panel de empleados
        user = getattr(self.request, 'user', None)
        try:
            if user is not None and user.groups.filter(name='Empleado').exists():
                return ['panel/empleado_password_change_form.html']
        except Exception:
            pass
        return [self.template_name]

    def form_valid(self, form):
        # Al cambiar la contraseña, limpiar el flag en Usuario
        resp = super().form_valid(form)
        try:
            usuario_custom = Usuario.objects.get(email__iexact=self.request.user.email)
            usuario_custom.must_change_password = False
            usuario_custom.save()
        except Usuario.DoesNotExist:
            pass
        # Si es empleado, redirigir al perfil/área de empleado
        try:
            if self.request.user.groups.filter(name='Empleado').exists():
                return redirect('panel:empleado_area_perfil')
        except Exception:
            pass
        return resp
