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
        model = Usuario
        fields = ['nombre', 'email', 'telefono', 'direccion']  # Los campos del modelo Usuario que pueden ser editados

class RegistroFormulario(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")

    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'telefono', 'direccion']  # Asegúrate de que estos sean los campos que deseas

    def clean_password2(self):
        """
        Verifica que las contraseñas coincidan.
        """
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cd['password2']

    def save(self, commit=True):
        """
        Guarda el usuario con la contraseña de forma segura.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])  # Establece la contraseña de forma segura
        if commit:
            user.save()  # Guarda el objeto Usuario en la base de datos
        return user
