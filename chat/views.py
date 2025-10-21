from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from django.utils.timezone import now
from .models import Chat, MensajeChat
from usuarios.models import Usuario
from productos.models import Producto, Categoria
from ventas.models import Venta, VentaDetalle
from django.db.models import Sum


def chat_widget(request):
	"""Renderiza el fragmento del widget de chat para incluir en el base.html.
	Si la plantilla no existe, la vista sigue disponible para integración.
	"""
	try:
		return render(request, 'chat/widget.html')
	except Exception:
		# Si no hay plantilla, devolvemos una respuesta sencilla
		return JsonResponse({'ok': False, 'error': 'widget template not found'}, status=404)


@csrf_exempt
def chat_send(request):
	"""Endpoint POST que recibe {'message': '...'} o {'option': '...'} y devuelve la respuesta del bot.

	Guarda los mensajes en los modelos `Chat` y `MensajeChat` cuando sea posible.
	Respuestas automáticas básicas (saludo, opciones, consultas simples).
	"""
	if request.method != 'POST':
		return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)

	try:
		payload = json.loads(request.body.decode('utf-8'))
	except Exception:
		return JsonResponse({'ok': False, 'error': 'JSON inválido'}, status=400)

	message = (payload.get('message') or '').strip()
	option = payload.get('option')
	usuario_id = payload.get('usuario_id')

	if not message and not option:
		return JsonResponse({'ok': False, 'error': 'Mensaje vacío'}, status=400)

	# Obtener (o crear) chat para el usuario si se envía usuario_id
	chat = None
	if usuario_id:
		try:
			user = Usuario.objects.get(pk=usuario_id)
			chat, _ = Chat.objects.get_or_create(usuario=user, estado='en_atencion')
		except Usuario.DoesNotExist:
			chat = None

	# Determinar la entrada del usuario (option tiene prioridad)
	user_text = option if option else message

	# Guardar el mensaje del usuario si tenemos chat
	if chat:
		try:
			MensajeChat.objects.create(chat=chat, remitente='Usuario', contenido=user_text)
		except Exception:
			# no bloqueamos por fallo en guardar
			pass

	# Lógica básica del bot
	text_lower = (user_text or '').lower()
	# Si se envió una opción como botón, priorizamos su interpretación
	if option:
		opt_lower = str(option).lower()
		# Productos / Categorías
		if 'product' in opt_lower or 'producto' in opt_lower or 'productos' in opt_lower:
			# Listar categorías como opciones (protegemos contra errores si la tabla no existe)
			try:
				cats = list(Categoria.objects.filter().order_by('nombre')[:6].values_list('nombre', flat=True))
			except Exception:
				cats = []
			if cats:
				reply = 'Selecciona una categoría:'
				suggested = list(cats)
			else:
				reply = 'No hay categorías disponibles. Escribe el nombre del producto que buscas.'
				suggested = []
			# respondimos ya a la opción
			if chat:
				try:
					MensajeChat.objects.create(chat=chat, remitente='Bot', contenido=reply)
				except Exception:
					pass
			return JsonResponse({'ok': True, 'reply': reply, 'suggested': suggested})

		# Categorías directas
		if 'categor' in opt_lower:
			try:
				cats = list(Categoria.objects.filter().order_by('nombre')[:6].values_list('nombre', flat=True))
			except Exception:
				cats = []
			if cats:
				reply = 'Categorías disponibles:'
				suggested = list(cats)
			else:
				reply = 'No hay categorías disponibles.'
				suggested = []
			if chat:
				try:
					MensajeChat.objects.create(chat=chat, remitente='Bot', contenido=reply)
				except Exception:
					pass
			return JsonResponse({'ok': True, 'reply': reply, 'suggested': suggested})

		# Promociones
		if 'promoc' in opt_lower:
			reply = 'Revisa nuestra sección de promociones en la web. Aquí solo muestro un recordatorio.'
			suggested = []
			if chat:
				try:
					MensajeChat.objects.create(chat=chat, remitente='Bot', contenido=reply)
				except Exception:
					pass
			return JsonResponse({'ok': True, 'reply': reply, 'suggested': suggested})

		# Delivery
		if 'delivery' in opt_lower or 'domicilio' in opt_lower:
			try:
				available = Producto.objects.filter(estado='activo', stock_actual__gt=0).exists()
			except Exception:
				available = False
			if available:
				reply = 'Sí, hacemos delivery. Indica tu ciudad para confirmar disponibilidad.'
				suggested = []
			else:
				reply = 'Por ahora no hay productos disponibles para delivery.'
				suggested = []
			if chat:
				try:
					MensajeChat.objects.create(chat=chat, remitente='Bot', contenido=reply)
				except Exception:
					pass
			return JsonResponse({'ok': True, 'reply': reply, 'suggested': suggested})

		# Información / Horarios
		if 'inform' in opt_lower or 'horario' in opt_lower or 'contacto' in opt_lower:
			reply = 'Nuestro horario es Lunes a Domingo 9:00-22:00. Puedes contactarnos al +123456789.'
			suggested = []
			if chat:
				try:
					MensajeChat.objects.create(chat=chat, remitente='Bot', contenido=reply)
				except Exception:
					pass
			return JsonResponse({'ok': True, 'reply': reply, 'suggested': suggested})
	if text_lower in ('hola', 'buenas', 'buenos dias', 'buenas tardes') or text_lower.startswith('hola'):
		reply = (
			'¡Buenos días! 👋\n'
			'Soy el asistente de Adonai. Puedo ayudarte con pedidos, productos, promociones y delivery.\n'
			'Elige una opción para comenzar:'
		)
		suggested = ['Productos', 'Categorías', 'Delivery', 'Información', 'Promociones']
	elif option == '1' or 'pedido' in text_lower:
		reply = 'Para consultarte el estado del pedido necesito tu número de pedido. Por favor escríbelo.'
		suggested = []
	elif option == '2' or 'producto' in text_lower or 'productos' in text_lower:
		# Listar categorías como opciones (protegemos contra errores si la tabla no existe)
		try:
			cats = list(Categoria.objects.filter().order_by('nombre')[:6].values_list('nombre', flat=True))
		except Exception:
			cats = []
		if cats:
			reply = 'Selecciona una categoría:'
			suggested = list(cats)
		else:
			# fallback: listar productos activos como sugerencia o usar opciones por defecto
			try:
				products = list(Producto.objects.filter(estado='activo', stock_actual__gt=0).order_by('-creado_en')[:6].values_list('nombre', flat=True))
			except Exception:
				products = []
			if products:
				reply = 'No encontré categorías, pero estos productos podrían interesarte:'
				suggested = list(products)
			else:
				reply = 'No hay categorías disponibles. Escribe el nombre del producto que buscas.'
				suggested = ['Empanadas', 'Bebidas', 'Otros']
	elif option == '3' or 'horario' in text_lower or 'contacto' in text_lower:
		reply = 'Nuestro horario es Lunes a Domingo 9:00-22:00. Puedes contactarnos al +123456789.'
		suggested = []
	else:
		# Respuesta fallback
		reply = 'Lo siento, no entendí eso. Puedes escribir "hola" para ver opciones o hacer una pregunta concreta.'
		suggested = []

	# Additional quick intents
	if 'promocion' in text_lower or 'promociones' in text_lower:
		# Si tuvieras un modelo Promocion, aquí lo consultarías. Por ahora devolvemos un stub.
		reply = 'Actualmente no hay promociones automáticas. Revisa la sección de promociones en el sitio.'
		suggested = []

	if 'lo mas vendido' in text_lower or 'mas vendido' in text_lower or 'top' in text_lower:
		# Obtener top 5 productos por cantidad vendida a partir de VentaDetalle
		try:
			top_qs = (VentaDetalle.objects.values('producto__nombre')
					  .annotate(total_cantidad=Sum('cantidad'))
					  .order_by('-total_cantidad')[:5])
			top_list = [f"{t['producto__nombre']} ({t['total_cantidad']})" for t in top_qs]
		except Exception:
			top_list = []
		if top_list:
			reply = 'Lo más vendido ahora:'
			suggested = top_list
		else:
			reply = 'Aún no hay datos de ventas para mostrar lo más vendido.'
			suggested = []

	if 'delivery' in text_lower or 'domicilio' in text_lower:
		# Comprobación simple de disponibilidad: si hay productos activos y stock
		try:
			available = Producto.objects.filter(estado='activo', stock_actual__gt=0).exists()
		except Exception:
			available = False
		if available:
			reply = 'Sí, hacemos delivery. Indica tu ciudad para confirmar disponibilidad.'
			suggested = []
		else:
			reply = 'Por ahora no hay productos disponibles para delivery.'
			suggested = []

	# Guardar respuesta del bot
	if chat:
		try:
			MensajeChat.objects.create(chat=chat, remitente='Bot', contenido=reply)
		except Exception:
			pass

	return JsonResponse({'ok': True, 'reply': reply, 'suggested': suggested})

