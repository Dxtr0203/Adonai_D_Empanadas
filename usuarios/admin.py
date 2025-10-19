from django.contrib import admin
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from .models import Rol, Usuario


class UsuarioAdminForm(forms.ModelForm):
	"""Formulario admin que permite editar/crear Usuario y sincronizar con User."""
	password_plain = forms.CharField(required=False, help_text='Dejar vacío para no cambiar la contraseña', widget=forms.PasswordInput)

	class Meta:
		model = Usuario
		fields = ['nombre', 'email', 'telefono', 'direccion', 'rol', 'estado']

	def save(self, commit=True):
		usuario = super().save(commit=False)
		pw = self.cleaned_data.get('password_plain')
		# Crear o actualizar usuario de auth
		username = usuario.email.lower()
		auth_user, created = User.objects.get_or_create(username=username, defaults={'email': usuario.email})
		if pw:
			auth_user.set_password(pw)
			auth_user.save()
			usuario.password = make_password(pw)
		else:
			# Si no se proporciona, no cambiar la contraseña en Usuario
			if usuario.pk is None:
				# Para nuevos usuarios, generar una contraseña random si no se puso
				auth_user.set_unusable_password()
				auth_user.save()

		# Asegurar que el email esté sincronizado
		if auth_user.email != usuario.email:
			auth_user.email = usuario.email
			auth_user.save()

		if commit:
			usuario.save()
		return usuario


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
	list_display = ('nombre', 'descripcion')
	search_fields = ('nombre',)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
	form = UsuarioAdminForm
	list_display = ('nombre', 'email', 'rol', 'estado', 'creado_en')
	list_filter = ('rol', 'estado')
	search_fields = ('nombre', 'email')
	ordering = ('-creado_en',)

