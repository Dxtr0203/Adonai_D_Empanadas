from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


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

	# Aquí podrías insertar lógica: guardar en modelos, llamar a API externa, etc.
	bot_reply = f"Bot: He recibido tu mensaje -> {message}"

	return JsonResponse({'ok': True, 'reply': bot_reply})

