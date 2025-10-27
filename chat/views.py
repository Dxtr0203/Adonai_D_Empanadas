from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re


def chat_widget(request):
	"""Renderiza el fragmento del widget de chat para incluir en el base.html."""
	return render(request, 'chat/widget.html')


@csrf_exempt
def chat_send(request):
	"""Endpoint POST que recibe {'message': '...'} y devuelve la respuesta del bot.

	Por ahora el bot es un echo simple que devuelve el mismo mensaje con prefijo.
	"""
	if request.method != 'POST':
		return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)

	try:
		payload = json.loads(request.body.decode('utf-8'))
		message = payload.get('message', '').strip()
	except Exception:
		return JsonResponse({'ok': False, 'error': 'JSON inválido'}, status=400)

	if not message:
		return JsonResponse({'ok': False, 'error': 'Mensaje vacío'}, status=400)

	# Respuestas predeterminadas en backend como fallback
	def normalize(s):
		import unicodedata
		return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()

	lc = normalize(message)

	# Lista de patrones (regex) y respuestas, usa límites de palabra para evitar coincidencias parciales
	predefined_patterns = [
		(r'\b(hola|buenos|buenas|saludo)\b', '¡Hola! 👋 Soy el asistente de Adonai. ¿En qué puedo ayudarte? Puedes preguntar por "información de la tienda", "productos", "servicios" o "horarios".'),
		(r'\b(informacion|datos tienda|info tienda)\b', 'Nuestra tienda está en La Paz, ofrecemos alimentos y accesorios para mascotas. ¿Quieres ver el catálogo? Visita la sección Catálogo.'),
		(r'\b(productos|catalogo|catalogo productos|productos disponibles)\b', 'Tenemos alimentos para perros y gatos, accesorios y juguetes. Puedes navegar el catálogo en la pestaña "Catálogo".'),
		(r'\b(servicios|servicio|servicios disponibles)\b', 'Ofrecemos delivery en la ciudad, asesoría para mascotas y pedidos por mayor. ¿Deseas más detalle sobre algún servicio?'),
		(r'\b(horario|horarios|abrimos|cerramos)\b', 'Nuestro horario es Lunes a Sábado de 9:00 a 19:00. Domingos 10:00 a 14:00.'),
		(r'\b(gracias|muchas gracias|thank)\b', '¡Con gusto! Si necesitas algo más, aquí estoy.'),
	]

	# Log simple al servidor para depuración
	print(f"[chat_send] message received: {message}")
	print(f"[chat_send] normalized: {lc}")

	for pattern, reply in predefined_patterns:
		try:
			if re.search(pattern, lc, flags=re.IGNORECASE):
				print(f"[chat_send] matched pattern: {pattern}")
				return JsonResponse({'ok': True, 'reply': reply})
		except re.error:
			# si el patrón está mal formateado, saltarlo
			continue

	# Fallback guardado/echo si no hay match
	bot_reply = f"Bot: He recibido tu mensaje -> {message}"
	return JsonResponse({'ok': True, 'reply': bot_reply})

