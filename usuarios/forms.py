# usuarios/forms.py
from django import forms
from .models import Usuario  # Asegúrate de que 'Usuario' sea el modelo correcto para los usuarios

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario  # El modelo de usuario
        fields = ['nombre', 'email', 'telefono', 'direccion']  # Los campos que el usuario puede editar
