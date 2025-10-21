from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import reverse


def checkout(request):
	"""Página de checkout: si no está autenticado redirige al registro con next.

	UX solicitado: llevar primero a 'registrarse' en vez de al login.
	La plantilla de registro proveerá un enlace 'Ya tengo cuenta' que lleva al login
	manteniendo el parámetro next para que, tras el login, el usuario vuelva al checkout.
	"""
	if not request.user.is_authenticated:
		register_url = reverse('usuarios:register')
		next_url = reverse('carrito:checkout')
		return redirect(f"{register_url}?next={next_url}")

	# Si está autenticado, mostrar el checkout
	return render(request, 'carrito/checkout.html')

# Create your views here.
