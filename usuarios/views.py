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

# Formulario simple para registro
class RegistroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")

    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'password', 'telefono', 'direccion']

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        pw2 = cleaned.get('password_confirm')
        if pw and pw2 and pw != pw2:
            raise forms.ValidationError('Las contraseñas no coinciden')
        return cleaned


def register(request):
    """Vista para registrar nuevos clientes."""
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            raw_password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            username_for_auth = email.lower()

            # Si ya existe un User con ese username/email, mostrar error
            if User.objects.filter(username=username_for_auth).exists():
                form.add_error('email', 'Ya existe una cuenta con este correo. Por favor inicia sesión o recupera tu contraseña.')
            else:
                # Crear el usuario de Django para que pueda autenticarse con LoginView
                user_auth = User.objects.create_user(username=username_for_auth, email=email, password=raw_password)

                usuario = form.save(commit=False)
                # Hashear la contraseña antes de guardar en el modelo Usuario
                usuario.password = make_password(raw_password)
                # Asignar rol 'Cliente' (crearlo si no existe)
                from .models import Rol
                rol_cliente, _created = Rol.objects.get_or_create(nombre='Cliente', defaults={'descripcion': 'Rol por defecto: Cliente'})
                usuario.rol = rol_cliente
                usuario.save()
                messages.success(request, 'Cuenta creada correctamente. Puedes iniciar sesión ahora.')
                return redirect('usuarios:login')
    else:
        form = RegistroForm()

    return render(request, 'usuarios/register.html', {'form': form})

# Vista personalizada de login
def custom_login(request):
    # Verifica los intentos fallidos (inicializar siempre para evitar UnboundLocalError)
    failed_attempts = request.session.get('failed_attempts', 0)
    last_failed_time_raw = request.session.get('last_failed_time', None)

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
                return redirect('usuarios:login')  # Redirige al login para intentar nuevamente después del bloqueo

        # Autentica al usuario
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Inicia sesión si las credenciales son correctas
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
            return redirect('usuarios:perfil')  # Redirige al perfil por defecto

        # Si el usuario no es válido, muestra el mensaje de error
        messages.error(request, "Credenciales incorrectas. Por favor, verifica tu usuario y contraseña.")
        
    # Incrementa los intentos fallidos
    request.session['failed_attempts'] = failed_attempts + 1
    # Guardar como ISO string para que sea serializable
    request.session['last_failed_time'] = timezone.now().isoformat()

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
