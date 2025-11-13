from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Usuario


# -------------------------
# LOGIN (CASE-INSENSITIVE)
# -------------------------
class LowercaseAuthenticationForm(AuthenticationForm):
    """Formulario de autenticación que convierte el usuario a minúsculas para evitar errores de mayúsculas."""
    def clean(self):
        username = self.cleaned_data.get('username')
        if username:
            self.cleaned_data['username'] = username.lower()
        return super().clean()


# -------------------------
# FORMULARIO PERFIL / EDICIÓN DE USUARIO
# -------------------------
class UsuarioForm(forms.ModelForm):
    """Formulario para editar datos del usuario."""
    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'telefono', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(+591) 7xx-xxxxxx'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección, ciudad, referencia'}),
        }


# -------------------------
# FORMULARIO DE REGISTRO
# -------------------------
class RegistroFormulario(forms.ModelForm):
    """Formulario de registro de nuevos usuarios."""
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
        label="Contraseña"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar Contraseña'}),
        label="Confirmar Contraseña"
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'telefono', 'direccion']

    def clean_password2(self):
        """Verifica que las contraseñas coincidan."""
        cd = self.cleaned_data
        if cd.get('password1') != cd.get('password2'):
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cd['password2']

    def save(self, commit=True):
        """Guarda el usuario con la contraseña encriptada."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


# -------------------------
# FORMULARIO DE CAMBIO DE CONTRASEÑA
# -------------------------
class PasswordChangeForm(forms.Form):
    """Formulario para cambio de contraseña."""
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña antigua'}),
        label="Contraseña antigua",
        required=True
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña nueva'}),
        label="Contraseña nueva",
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}),
        label="Confirmación de contraseña",
        required=True
    )

    def clean_new_password(self):
        """Valida la contraseña nueva usando las reglas de Django (longitud, fortaleza, etc.)."""
        new_password = self.cleaned_data.get('new_password')
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)
        return new_password

    def clean(self):
        """Verifica que las contraseñas nuevas coincidan."""
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', "Las contraseñas no coinciden.")
        return cleaned_data
