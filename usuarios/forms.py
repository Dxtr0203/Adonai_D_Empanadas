# usuarios/forms.py
from django import forms
from .models import Usuario  # Asegúrate de que 'Usuario' sea el modelo correcto para los usuarios
from django.contrib.auth.forms import AuthenticationForm


class LowercaseAuthenticationForm(AuthenticationForm):
    """AuthenticationForm that lowercases the username before authenticating.

    This helps when we use email-as-username and want login to be case-insensitive.
    """
    def clean(self):
        username = self.cleaned_data.get('username')
        if username:
            self.cleaned_data['username'] = username.lower()
        return super().clean()

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario  # El modelo de usuario
        fields = ['nombre', 'email', 'telefono', 'direccion']  # Los campos que el usuario puede editar
