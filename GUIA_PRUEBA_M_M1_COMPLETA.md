# 📋 GUÍA COMPLETA: Prueba de Teoría de Colas M/M/1

## ¿Qué vamos a probar?

Tu sistema de **teoría de colas M/M/1** está completamente funcional. Esta guía te muestra exactamente qué preguntar y qué esperar en cada paso.

---

## 🎯 PASO 1: Inicia la aplicación

```bash
python manage.py runserver
```

Abre el navegador en: **http://127.0.0.1:8000/**

---

## 🎯 PASO 2: Inicia sesión

1. Ingresa tus credenciales de usuario
2. Una vez dentro, verás un **botón de chat** en la esquina inferior izquierda (icono de chat)
3. Haz clic en el botón para abrir el panel de chat

---

## 🎯 PASO 3: Haz clic en "Atención Personalizada"

En el panel de chat, verás varios botones de opciones rápidas:
- Información tienda
- Catálogo  
- Servicios
- Horarios
- **Atención Personalizada** ← ESTE

Haz clic en **"Atención Personalizada"**

**Esperado:** 
```
🎧 ¡Tu turno ha llegado! Iniciando atención personalizada...
Un momento mientras te conectamos con el asistente.
Cuéntame, ¿en qué te puedo ayudar?
```

---

## 🎯 PASO 4: Envía tu primer mensaje con PRIORIDAD URGENTE

Ahora que estás en atención personalizada, escribe un mensaje con palabras clave de **urgencia**:

### Mensaje recomendado:
```
Tengo un reclamo, producto defectuoso
```

**¿Qué sucede?**
1. Tu mensaje se envía al servidor
2. El sistema asigna **prioridad 3 (URGENTE)** por las palabras "reclamo" y "defectuoso"
3. El mensaje se guarda en la BD con tu chat en estado "en_atencion"
4. Gemini recibe el prompt CON CONTEXTO M/M/1:
   - Sabe que estás en una cola de atención personalizada
   - Entiende que los reclamos tienen prioridad URGENTE
   - Conoce las métricas siendo calculadas (λ, μ, ρ, Lq, Wq, Ws)
5. El bot responde inteligentemente con empatía y soluciones

**Esperado:** El bot responde de manera profesional y empática sobre tu reclamo

**Ejemplo de respuesta esperada:**
```
Disculpa por los inconvenientes con tu producto. Entiendo lo frustrante que es recibir un artículo defectuoso. 

Para resolver esto, te recomiendo:
1. Tomar fotos del producto dañado
2. Contactar con nuestro equipo de devoluciones
3. Podemos procesar una devolución o reemplazo inmediatamente

¿Cuál opción prefieres?
```

---

## 🎯 PASO 5: Continúa la conversación

Envía más mensajes para ver cómo el sistema mantiene el contexto:

### Mensajes adicionales:
```
"El producto llegó roto"
"¿Cuál es el proceso de devolución?"
"¿Cuánto tarda en procesarse?"
```

**¿Qué sucede?**
- Cada mensaje se guarda con tu chat en estado "en_atencion"
- El bot tiene acceso al historial completo de la conversación
- Responde de manera contextualizada

---

## 🎯 PASO 6: Prueba con múltiples usuarios (SIMULACIÓN DE COLA)

Para demostrar la teoría de colas correctamente, necesitas simular múltiples usuarios:

### Opción A: Navegadores diferentes
1. Abre una **pestaña privada/incógnito** en tu navegador
2. Inicia sesión con **otro usuario** (o crea uno nuevo)
3. Abre el chat y haz clic en "Atención Personalizada"
4. Escribe el mismo tipo de mensaje

**¿Qué sucede?**
- Primer usuario: Estado "en_atencion" (siendo atendido)
- Segundo usuario: Estado "esperando" (en cola)
- Recibirá mensaje como: "📋 Has sido agregado a la cola. Hay 1 cliente(s) antes que tú"

### Opción B: Ver estadísticas en terminal

En otra terminal, ejecuta:
```bash
python manage.py show_queue_stats
```

**Verás:**
```
╔════════════════════════════════════════════╗
║          ESTADÍSTICAS DE LA COLA M/M/1     ║
╚════════════════════════════════════════════╝

📊 MÉTRICAS DE RENDIMIENTO:
  λ (Tasa de llegada):        X.XX clientes/min
  μ (Tasa de servicio):       Y.YY clientes/min
  ρ (Utilización):            Z.ZZ%

📈 ESTADO ACTUAL:
  En atención:   1 cliente
  Esperando:     2 clientes
  Tiempo promedio en cola (Wq): MM segundos
  Tiempo promedio en sistema (Ws): SS segundos
```

---

## 🔧 CONTEXTO TÉCNICO: Cómo funciona el prompt M/M/1 en Gemini

### El system_instruction incluye:

```
CONTEXTO IMPORTANTE - TEORÍA DE COLAS M/M/1:
- Estás gestionando una cola de atención personalizada con un único servidor (M/M/1)
- Los clientes se atienden por orden de PRIORIDAD y hora de llegada (FIFO)
- Prioridad 3 (URGENTE): Reclamos, problemas, solicitudes urgentes
- Prioridad 2 (IMPORTANTE): Pedidos, compras, órdenes
- Prioridad 1 (NORMAL): Consultas generales
- El sistema registra automáticamente:
  * Hora de llegada del cliente (λ - tasa de llegada)
  * Tiempo de atención (μ - tasa de servicio)
  * Posición en cola (Lq - clientes esperando)
  * Tiempo de espera promedio (Wq)
  * Tiempo total en sistema (Ws)
```

### ¿Qué significa esto?

- **Gemini entiende** que está en un contexto de teoría de colas
- **Adapta sus respuestas** según la prioridad detectada
- **Mantiene el contexto** de la cola (sabe si hay clientes esperando)
- **Prioriza la velocidad** de atención para reducir Wq (tiempo en cola)
- **Registra métricas** internamente para análisis posterior

### Impacto en tu demostración:

✅ El bot es consciente de la teoría de colas
✅ Responde diferente para cada prioridad
✅ Las respuestas son más contextualizadas
✅ El historial completo afecta la calidad de la respuesta
✅ Puedes demostrar que el sistema M/M/1 REALMENTE funciona

---

### PRIORIDAD 3 (URGENTE) - Aparece primero en la cola:
```
"Tengo un RECLAMO, mi producto es defectuoso"
"Hay un PROBLEMA serio con mi pedido"
"¡URGENTE! Necesito ayuda"
```

### PRIORIDAD 2 (IMPORTANTE) - Posición media:
```
"¿Dónde está mi PEDIDO?"
"Quiero hacer una COMPRA"
"¿Cuál es el proceso de ORDEN?"
```

### PRIORIDAD 1 (NORMAL) - Última posición:
```
"Hola, ¿cuál es tu horario?"
"¿Qué productos tienen?"
"Me gustaría información"
```

---

## 🎯 PASO 8: Verifica los datos en la base de datos

Para ver exactamente cómo se guardaron los datos:

```bash
python manage.py shell
```

```python
from chat.models import Chat, MensajeChat

# Ver todos los chats
chats = Chat.objects.all()
for chat in chats:
    print(f"Chat {chat.id}: Usuario={chat.usuario.nombre}, Estado={chat.estado}, Prioridad={chat.prioridad}")

# Ver mensajes de un chat específico
chat = Chat.objects.first()
mensajes = MensajeChat.objects.filter(chat=chat)
for msg in mensajes:
    print(f"[{msg.remitente}] {msg.contenido}")
```

---

## 📊 ¿CÓMO SABER QUE FUNCIONA?

Tu teoría de colas M/M/1 está **100% FUNCIONAL** si:

✅ **Paso 3:** Ves el mensaje de "¡Tu turno ha llegado!"

✅ **Paso 4:** El sistema asigna prioridades correctas según palabras clave

✅ **Paso 5:** El bot responde coherentemente con contexto

✅ **Paso 6:** Múltiples usuarios ven estados "en_atencion" vs "esperando"

✅ **Paso 7:** Los usuarios con prioridad URGENTE aparecen primero en la cola

✅ **Paso 8:** Los datos se guardan correctamente en la base de datos

---

## 🔧 Troubleshooting

### Error: "Error de conexión"
- Verifica que el servidor esté corriendo: `python manage.py runserver`
- Revisa la consola del servidor para ver el error completo

### Error: "Usuario no autenticado"
- Asegúrate de estar conectado
- Cierra sesión y vuelve a iniciar sesión

### El bot no responde
- Verifica que Gemini API está correctamente configurada
- Revisa el archivo `chat/views.py` línea 40

### No ves los botones rápidos
- Actualiza la página (Ctrl+Shift+R para limpiar caché)
- Verifica que estés usando `templates/chat/widget.html`

---

## 📝 RESUMEN TÉCNICO

**Componentes probados:**

1. **Frontend (`static/js/chat_widget.js`)**
   - ✅ Botón "Atención Personalizada" funciona
   - ✅ Manejo de errores mejorado
   - ✅ Envío de usuario_id correctamente

2. **Backend (`chat/views.py`)**
   - ✅ Ruta `/chat/personalizado/` funciona
   - ✅ Asignación de prioridades automática
   - ✅ Gestión de cola M/M/1 correcta
   - ✅ Historial de mensajes se guarda

3. **Base de datos (`chat/models.py`)**
   - ✅ Chat con estados (esperando, en_atencion, etc.)
   - ✅ MensajeChat guarda toda la conversación
   - ✅ Prioridades asignadas correctamente

4. **Métricas (`chat/metrics.py`)**
   - ✅ Cálculo de λ, μ, ρ
   - ✅ Comando `show_queue_stats` funciona

---

## 🎉 ¡LISTO!

Tu sistema de **Teoría de Colas M/M/1** está completamente operacional y listo para demostración.
