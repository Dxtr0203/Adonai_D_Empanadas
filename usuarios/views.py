from django.shortcuts import render, redirect, resolve_url
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from django.urls import reverse_lazy
from django import forms
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.db import models

from .models import Usuario
from .forms import UsuarioForm, PasswordChangeForm, ClientePasswordChangeForm


# ======================
# FORMULARIO DE REGISTRO
# ======================
class RegistroForm(forms.ModelForm):
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

        # Si no se proporciona, usar contraseña por defecto
        if not pw and not pw2:
            cleaned['password'] = cleaned['password_confirm'] = 'clientes123'

        if cleaned['password'] != cleaned['password_confirm']:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned


def register(request):
    """Vista para registrar nuevos clientes."""
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            raw_password = form.cleaned_data.get('password') or 'clientes123'
            email = form.cleaned_data['email']
            username_for_auth = email.lower()

            # Evita duplicados
            if User.objects.filter(username=username_for_auth).exists() or Usuario.objects.filter(email__iexact=email).exists():
                form.add_error('email', 'Ya existe una cuenta con este correo.')
            else:
                # Crear usuario personalizado
                from .models import Rol
                rol_cliente, _ = Rol.objects.get_or_create(nombre='Cliente', defaults={'descripcion': 'Rol por defecto: Cliente'})
                usuario = form.save(commit=False)
                usuario.password = make_password(raw_password)
                usuario.rol = rol_cliente
                usuario.save()

                # Crear auth.User sincronizado
                user_auth = User.objects.create_user(username=username_for_auth, email=email, password=raw_password)
                user_auth.is_active = (usuario.estado == 'activo')
                user_auth.save()

                messages.success(request, 'Cuenta creada correctamente. Por favor inicia sesión.')
                return redirect('usuarios:login')
    else:
        form = RegistroForm()

    return render(request, 'usuarios/register.html', {'form': form})


# ======================
# LOGIN PERSONALIZADO
# ======================
def custom_login(request):
    failed_attempts = request.session.get('failed_attempts', 0)
    last_failed_time_raw = request.session.get('last_failed_time')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        last_failed_time = parse_datetime(last_failed_time_raw) if isinstance(last_failed_time_raw, str) else last_failed_time_raw
        if last_failed_time and timezone.is_naive(last_failed_time):
            last_failed_time = timezone.make_aware(last_failed_time, timezone.get_current_timezone())

        if failed_attempts >= getattr(settings, 'LOGIN_FAILURE_LIMIT', 5) and last_failed_time:
            time_since_last = timezone.now() - last_failed_time
            if time_since_last.total_seconds() < getattr(settings, 'LOGIN_BLOCK_TIME', 60):
                messages.error(request, f"Demasiados intentos. Intenta en unos segundos.")
                return render(request, 'usuarios/login.html')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            request.session['failed_attempts'] = 0
            request.session['last_failed_time'] = None

            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}):
                return redirect(next_url)

            # Redirecciones según tipo
            if user.is_superuser:
                return redirect('panel:dashboard')
            if user.groups.filter(name='Empleado').exists():
                usuario_custom = Usuario.objects.filter(email__iexact=user.email).first()
                if usuario_custom and getattr(usuario_custom, 'must_change_password', False):
                    return redirect('usuarios:force_password_change')
                return redirect('panel:empleado_area_dashboard')
            return redirect('inicio')

        # Falla login
        messages.error(request, "Credenciales incorrectas.")
        request.session['failed_attempts'] = failed_attempts + 1
        request.session['last_failed_time'] = timezone.now().isoformat()

    return render(request, 'usuarios/login.html')


# ======================
# PERFIL DE USUARIO
# ======================
@login_required
def perfil(request):
    try:
        usuario = Usuario.objects.get(email__iexact=request.user.email)
    except Usuario.DoesNotExist:
        usuario = None

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            user_obj = form.save(commit=False)
            if usuario:
                user_obj.id = usuario.id
            user_obj.save()

            # Sincroniza con auth.User
            auth_user = User.objects.filter(email__iexact=request.user.email).first()
            if auth_user:
                new_email = form.cleaned_data.get('email')
                if new_email and new_email.lower() != auth_user.email.lower():
                    auth_user.email = new_email.lower()
                    auth_user.username = new_email.lower()
                    auth_user.save()

            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('usuarios:perfil')
    else:
        form = UsuarioForm(instance=usuario or None)

    return render(request, 'usuarios/perfil.html', {'form': form, 'usuario_obj': usuario})


# ======================
# CAMBIO FORZADO DE CONTRASEÑA
# ======================
@login_required
def force_password_change(request):
    """Vista para forzar cambio de contraseña (empleados o usuarios)."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['new_password'])
            user.save()

            # Actualizar sesión para no desconectar al usuario
            update_session_auth_hash(request, user)

            # Marcar en modelo Usuario que ya cambió la contraseña
            try:
                usuario_custom = Usuario.objects.get(email__iexact=user.email)
                usuario_custom.must_change_password = False
                usuario_custom.save()
            except Usuario.DoesNotExist:
                pass

            messages.success(request, "¡Contraseña actualizada exitosamente!")
            return redirect('usuarios:perfil')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = PasswordChangeForm()

    return render(request, 'usuarios/force_password_change.html', {'form': form})


# ======================
# CAMBIAR CONTRASEÑA (CLIENTE)
# ======================
@login_required
def cambiar_contrasena_cliente(request):
    """Vista AJAX para que el cliente cambie su contraseña desde el perfil."""
    if request.method == 'POST':
        form = ClientePasswordChangeForm(request.POST)
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data['old_password']
            
            # Verificar que la contraseña antigua es correcta
            if not user.check_password(old_password):
                return render(request, 'usuarios/modal_cambiar_contrasena.html', 
                            {'form': form, 'error': 'La contraseña actual es incorrecta.'}, 
                            status=400)
            
            # Cambiar la contraseña
            new_password = form.cleaned_data['new_password']
            
            # 1. Actualizar en auth.User
            user.set_password(new_password)
            user.save()
            
            # 2. Actualizar en tabla usuarios (custom)
            try:
                usuario_custom = Usuario.objects.get(email__iexact=user.email)
                # Usar el mismo hash que Django genera para sincronizar
                usuario_custom.password = user.password  # Usar el hash generado por set_password
                usuario_custom.actualizado_en = timezone.now()
                usuario_custom.save(update_fields=['password', 'actualizado_en'])
            except Usuario.DoesNotExist:
                pass
            
            # 3. Actualizar sesión para no desconectar al usuario
            update_session_auth_hash(request, user)
            
            # Retornar respuesta exitosa
            return render(request, 'usuarios/modal_cambiar_contrasena.html', 
                        {'form': ClientePasswordChangeForm(), 'success': 'Contraseña actualizada correctamente.'})
        else:
            return render(request, 'usuarios/modal_cambiar_contrasena.html', 
                        {'form': form}, status=400)
    else:
        form = ClientePasswordChangeForm()
    
    return render(request, 'usuarios/modal_cambiar_contrasena.html', {'form': form})


# ======================
# LOGOUT PERSONALIZADO
# ======================
@login_required
def custom_logout(request):
    """Cierra la sesión completamente y redirige a inicio."""
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect('inicio')


# ======================
# RECUPERACIÓN DE CONTRASEÑA
# ======================
def recovery_verify(request):
    """Verifica usuario y teléfono para recuperación de contraseña."""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            phone = data.get('phone', '').strip()

            # Buscar usuario por nombre o email
            usuario = Usuario.objects.filter(
                models.Q(nombre__icontains=username) | 
                models.Q(email__icontains=username)
            ).first()

            if not usuario:
                return JsonResponse({
                    'success': False,
                    'message': 'Usuario no encontrado.'
                })

            # El teléfono siempre será 75257525 para propósitos de demostración
            # En producción, verificarías que coincida con el teléfono registrado
            request.session['recovery_username'] = username
            request.session['recovery_phone'] = '75257525'  # Teléfono fijo para la demostración
            request.session['recovery_user_id'] = usuario.id

            return JsonResponse({
                'success': True,
                'message': 'Usuario verificado. Código de 6 dígitos enviado al teléfono.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


def recovery_verify_code(request):
    """Verifica el código de recuperación y cambia la contraseña."""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            code = data.get('code', '').strip()
            password = data.get('password', '').strip()
            username = data.get('username', '').strip()

            # Código predeterminado: QWE123
            RECOVERY_CODE = 'QWE123'
            
            if code != RECOVERY_CODE:
                return JsonResponse({
                    'success': False,
                    'message': 'Código inválido. El código correcto es QWE123.'
                })

            # Buscar usuario
            usuario = Usuario.objects.filter(
                models.Q(nombre__icontains=username) | 
                models.Q(email__icontains=username)
            ).first()

            if not usuario:
                return JsonResponse({
                    'success': False,
                    'message': 'Usuario no encontrado.'
                })

            # Cambiar contraseña en tabla Usuario
            usuario.password = make_password(password)
            usuario.save(update_fields=['password'])

            # Cambiar contraseña en auth.User
            auth_user = User.objects.filter(email__iexact=usuario.email).first()
            if auth_user:
                auth_user.set_password(password)
                auth_user.save()

            # Limpiar sesión
            if 'recovery_username' in request.session:
                del request.session['recovery_username']
            if 'recovery_phone' in request.session:
                del request.session['recovery_phone']
            if 'recovery_user_id' in request.session:
                del request.session['recovery_user_id']

            return JsonResponse({
                'success': True,
                'message': 'Contraseña actualizada correctamente.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


def recovery_verify_code_only(request):
    """Verifica solo el código (sin cambiar contraseña) y crea sesión temporal."""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            code = data.get('code', '').strip()
            username = data.get('username', '').strip()

            # Código predeterminado: QWE123
            RECOVERY_CODE = 'QWE123'
            
            if code != RECOVERY_CODE:
                return JsonResponse({
                    'success': False,
                    'message': 'Código inválido. El código correcto es QWE123.'
                })

            # Buscar usuario
            usuario = Usuario.objects.filter(
                models.Q(nombre__icontains=username) | 
                models.Q(email__icontains=username)
            ).first()

            if not usuario:
                return JsonResponse({
                    'success': False,
                    'message': 'Usuario no encontrado.'
                })

            # Iniciar sesión del usuario (para que acceda al perfil)
            auth_user = User.objects.filter(email__iexact=usuario.email).first()
            if auth_user:
                # Crear sesión manualmente
                from django.contrib.auth import login as django_login
                # Esto se hará desde el frontend redireccionando, así que solo confirmamos
                request.session['recovery_user_email'] = auth_user.email
                request.session.save()

            return JsonResponse({
                'success': True,
                'message': 'Código verificado. Redirigiendo al perfil...'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})
