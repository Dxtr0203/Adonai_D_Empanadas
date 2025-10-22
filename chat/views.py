from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import connection
import logging
from django.utils.timezone import now
from django.conf import settings
from django.db.models import Sum

from .models import Chat, MensajeChat  # Asume que estos modelos están definidos
from usuarios.models import Usuario    # Asume que este modelo está definido
from productos.models import Producto, Categoria  # Asume que estos modelos están definidos
from ventas.models import VentaDetalle  # Asume que este modelo está definido

# Gemini 2.5 imports
from google import genai
from google.genai.errors import APIError

logger = logging.getLogger(__name__)

# Crear cliente Gemini 2.5
# Asegúrate de que settings.GEMINI_API_KEY esté configurado en settings.py

client = genai.Client(api_key="AIzaSyAvIvQpRW6qL3ZqWtU8LY1o_RJjTeFrucs")
try:
    print("Inicializando cliente Gemini 2.5...")
    logger.info("Cliente Gemini 2.5 inicializado correctamente.")
except Exception:
    # Manejo básico si la clave no está disponible al inicio
    logger.error("La clave GEMINI_API_KEY no está configurada correctamente.")
    client = None

# ===========================
# FUNCIONES AUXILIARES
# ===========================

def chat_widget(request):
    """Renderiza el fragmento del widget de chat."""
    try:
        return render(request, 'chat/widget.html')
    except Exception:
        return JsonResponse({'ok': False, 'error': 'widget template not found'}, status=404)


def get_user_data(user_id):
    """Obtiene datos de usuario usando SQL directo."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT nombre, email FROM usuarios_usuario WHERE id = %s", [user_id])
        row = cursor.fetchone()
        if row:
            return {"nombre": row[0], "email": row[1]}
        return None


def get_categories():
    logger.debug("Obteniendo categorías de productos...")
    """Obtiene categorías de productos usando SQL directo."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT nombre FROM productos_categoria ORDER BY nombre LIMIT 6")
        return [row[0] for row in cursor.fetchall()]


def get_top_products():
    """Obtiene los productos con mayor stock usando SQL directo."""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT nombre FROM productos_producto WHERE estado = 'activo' AND stock_actual > 0 ORDER BY stock_actual DESC LIMIT 6"
        )
        return [row[0] for row in cursor.fetchall()]


def get_gemini_response(prompt, history=[]):
    """
    Genera una respuesta usando la API Gemini 2.5, incluyendo el historial.
    
    El historial debe ser una lista de {'role': 'Usuario'/'Bot', 'text': '...'}
    """
    if not client:
        return "El asistente inteligente no está disponible debido a un error de configuración."

    try:
        # 1. Instrucción de sistema para el modelo
        system_instruction = (
            "Eres Adonai, un asistente de chat amigable y profesional para una tienda de "
            "comida/productos. Tu rol principal es ayudar con pedidos, productos, promociones, "
            "delivery e información de contacto. Mantén tus respuestas concisas y claras. "
            "Cuando se te pregunte por un tema que tienes cubierto en la lógica interna (ej. 'delivery', 'horario'), "
            "responde de forma genérica o amigable, y recuerda al usuario que la información detallada está en la web si no puedes proveerla directamente."
            "El contexto del historial es importante para mantener la conversación."
        )
        
        # 2. Construir la estructura de 'contents' para la API de Gemini
        contents = []
        
        # Agregar el historial
        for message in history:
            # Gemini espera 'user' o 'model' (que representa al bot) como roles
            role = 'user' if message['role'] == 'Usuario' else 'model'
            contents.append({'role': role, 'parts': [{'text': message['text']}]})
            
        # Agregar el mensaje actual del usuario (el prompt)
        contents.append({'role': 'user', 'parts': [{'text': prompt}]})
        
        # 3. Llamar a la API
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents, # Se envía el historial completo
            config={"system_instruction": system_instruction}
        )
        
        return response.text.strip() if response and response.text else "No pude generar una respuesta."
        
    except APIError as e:
        logger.error(f"Error en Gemini API (APIError): {e}")
        return "Hubo un problema al conectar con el asistente inteligente. Por favor, inténtalo de nuevo."
    except Exception as e:
        logger.error(f"Error en Gemini API: {e}")
        return "Hubo un problema desconocido al procesar tu solicitud."


# ===========================
# VISTA PRINCIPAL DEL CHAT
# ===========================

@csrf_exempt
def chat_send(request):
    """Endpoint POST que recibe {'message': '...'} o {'option': '...'} y devuelve la respuesta del bot."""
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

    # Obtener o crear chat
    chat = None
    if usuario_id:
        try:
            # Usar .select_related() para evitar consultas N+1 si el modelo Chat accede a Usuario
            user = Usuario.objects.get(pk=usuario_id)
            # 'en_atencion' es el estado que indica que el chat está activo.
            chat, _ = Chat.objects.get_or_create(usuario=user, estado='en_atencion')
        except Usuario.DoesNotExist:
            chat = None

    user_text = option if option else message
    reply = None
    suggested = []
    
    # Si es una respuesta de la lógica interna, guardar mensaje del usuario AHORA
    # Si es para Gemini (else), lo guardamos MÁS TARDE para asegurar que el historial sea preciso.
    is_internal_reply = False 

    text_lower = (user_text or '').lower()

    # ===========================
    # LÓGICA INTERNA DEL BOT (Respuestas rápidas y estructuradas)
    # ===========================
    if option:
        opt_lower = str(option).lower()
        is_internal_reply = True 

        if 'product' in opt_lower or 'producto' in opt_lower or 'productos' in opt_lower or 'categor' in opt_lower:
            try:
                cats = list(Categoria.objects.order_by('nombre')[:6].values_list('nombre', flat=True))
            except Exception:
                cats = []
            
            if cats:
                reply = 'Selecciona una categoría o escribe el nombre del producto que buscas:'
                suggested = list(cats)
            else:
                reply = 'No hay categorías disponibles. Escribe el nombre del producto que buscas.'
                suggested = []
        
        elif 'promoc' in opt_lower:
            reply = 'Revisa nuestra sección de promociones en la web. Aquí solo te daré un recordatorio.'
            suggested = []

        elif 'delivery' in opt_lower or 'domicilio' in opt_lower:
            try:
                available = Producto.objects.filter(estado='activo', stock_actual__gt=0).exists()
            except Exception:
                available = False
                
            if available:
                reply = 'Sí, hacemos delivery. Indica tu ciudad para confirmar disponibilidad.'
            else:
                reply = 'Por ahora no hay productos disponibles para delivery.'
            suggested = []

        elif 'inform' in opt_lower or 'horario' in opt_lower or 'contacto' in opt_lower:
            reply = 'Nuestro horario es Lunes a Domingo 9:00-22:00. Puedes contactarnos al +123456789.'
            suggested = []

    # ===========================
    # SALUDOS Y RESPUESTAS BÁSICAS (Por texto o por opción simple)
    # ===========================
    elif text_lower in ('hola', 'buenas', 'buenos dias', 'buenas tardes') or text_lower.startswith('hola'):
        is_internal_reply = True 
        reply = (
            '¡Buenos días! 👋\n'
            'Soy el asistente de Adonai. Puedo ayudarte con pedidos, productos, promociones y delivery.\n'
            'Elige una opción para comenzar:'
        )
        suggested = ['Productos', 'Categorías', 'Delivery', 'Información', 'Promociones']

    elif 'pedido' in text_lower:
        is_internal_reply = True 
        reply = 'Para consultarte el estado del pedido necesito tu número de pedido. Por favor escríbelo.'
        suggested = []
    
    elif 'lo mas vendido' in text_lower or 'mas vendido' in text_lower or 'top' in text_lower:
        is_internal_reply = True 
        try:
            top_qs = (VentaDetalle.objects.values('producto__nombre')
                      .annotate(total_cantidad=Sum('cantidad'))
                      .order_by('-total_cantidad')[:5])
            top_list = [f"{t['producto__nombre']} ({t['total_cantidad']} vendidas)" for t in top_qs]
        except Exception:
            top_list = []
            
        if top_list:
            reply = 'Lo más vendido ahora:'
            suggested = top_list
        else:
            reply = 'Aún no hay datos de ventas para mostrar lo más vendido.'
            suggested = []

    elif 'delivery' in text_lower or 'domicilio' in text_lower:
        is_internal_reply = True 
        try:
            available = Producto.objects.filter(estado='activo', stock_actual__gt=0).exists()
        except Exception:
            available = False
            
        if available:
            reply = 'Sí, hacemos delivery. Indica tu ciudad para confirmar disponibilidad.'
        else:
            reply = 'Por ahora no hay productos disponibles para delivery.'
        suggested = []

    else:
        # 🧠 Respuesta inteligente con Gemini 2.5 (Si no cae en ninguna regla interna)
        
        # 1. Obtener historial (últimos 9 mensajes ANTERIORES)
        history_for_gemini = []
        if chat:
            # Se obtienen los últimos 9 mensajes, ordenados de más antiguo a más reciente
            recent_messages_qs = MensajeChat.objects.filter(chat=chat).order_by('-creado_en')[:9]
            # Invertir la lista para orden cronológico (de antiguo a nuevo)
            recent_messages = list(reversed(recent_messages_qs))
            
            history_for_gemini = [
                {'role': msg.remitente, 'text': msg.contenido} 
                for msg in recent_messages
            ]

        # 2. Llamar a la función Gemini con el historial
        reply = get_gemini_response(user_text, history=history_for_gemini)
        suggested = []


    # ===========================
    # GUARDAR MENSAJES Y RESPONDER
    # ===========================
    
    # 1. Guardar mensaje del usuario (solo si el chat existe)
    if chat:
        try:
            # Solo se crea si no fue creado antes por un camino de lógica interna
            if is_internal_reply:
                 MensajeChat.objects.get_or_create(chat=chat, remitente='Usuario', contenido=user_text)
            else:
                 # Si vino por Gemini, el mensaje del usuario no se ha guardado
                 MensajeChat.objects.create(chat=chat, remitente='Usuario', contenido=user_text)
        except Exception as e:
            logger.error(f"Error al guardar mensaje del usuario: {e}")
            pass

    # 2. Guardar respuesta del bot (solo si el chat existe y hay una respuesta)
    if chat and reply:
        try:
            MensajeChat.objects.create(chat=chat, remitente='Bot', contenido=reply)
        except Exception as e:
            logger.error(f"Error al guardar mensaje del bot: {e}")
            pass

    logger.debug(f"Usuario ID: {usuario_id}, Mensaje: {message}, Opción: {option}")
    logger.debug(f"Respuesta del bot: {reply}, Opciones sugeridas: {suggested}")

    return JsonResponse({'ok': True, 'reply': reply, 'suggested': suggested})