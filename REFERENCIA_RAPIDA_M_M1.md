# ⚡ REFERENCIA RÁPIDA: SISTEMA M/M/1

## 📍 UBICACIÓN
- **Carpeta principal:** `chat/`
- **Archivos clave:**
  - `models.py` - Modelo Chat
  - `views.py` - Funciones chat_personalizado, procesar_cola
  - `metrics.py` - Cálculos M/M/1
  - `urls.py` - Endpoint /chat/personalizado/

---

## 🚀 INICIAR RÁPIDAMENTE

```bash
# 1. Iniciar servidor
python manage.py runserver

# 2. Ver estadísticas
python manage.py show_queue_stats

# 3. Abrir navegador
http://127.0.0.1:8000
# → Inicia sesión → Haz clic en Chat → "Atención Personalizada"
```

---

## 📊 FÓRMULAS M/M/1

```
λ = Tasa de llegada (clientes/hora)
μ = Tasa de servicio (clientes/hora)
ρ = λ / μ (utilización, debe ser < 1)

Lq = ρ² / (1 - ρ)     [Promedio en cola]
Wq = Lq / λ           [Tiempo en cola]
Ws = 1 / (μ - λ)      [Tiempo total]
```

---

## 🔧 COMANDOS ÚTILES

```bash
# Ver métricas
python manage.py show_queue_stats
python manage.py show_queue_stats --horas 48
python manage.py show_queue_stats --cola

# Acceder a shell
python manage.py shell

# Ejecutar pruebas
python manage.py shell < chat/quick_test.py

# Hacer check
python manage.py check
```

---

## 💻 CÓDIGO RÁPIDO (Django Shell)

```python
# Importar
from chat.models import Chat, MensajeChat
from chat.metrics import calcular_metricas, obtener_estadisticas_cola
from usuarios.models import Usuario

# Ver cola actual
chats = Chat.objects.filter(estado='esperando').order_by('llegada')
print(f"En cola: {chats.count()}")

# Ver métricas
metricas = calcular_metricas(horas_atras=24)
print(metricas)

# Ver estadísticas
stats = obtener_estadisticas_cola()
print(stats)

# Crear chat de prueba
usuario = Usuario.objects.first()
chat = Chat.objects.create(
    usuario=usuario,
    estado='esperando',
    prioridad=3
)
print(f"Chat creado: {chat.id}")
```

---

## 🎯 FLUJO DE USUARIO

```
1. Usuario solicita "Atención Personalizada"
   ↓
2. POST a /chat/personalizado/
   ↓
3. Backend asigna prioridad
   ↓
4. procesar_cola() decide si atender o encolar
   ↓
5. Usuario ve: "Tu turno ha llegado" O "Posición X en cola"
```

---

## 📈 MÉTRICAS RETORNADAS

```python
{
    'λ (Tasa llegada)': 0.5,              # clientes/hora
    'μ (Tasa servicio)': 2.0,             # clientes/hora
    'ρ (Utilización)': 0.25,              # 25% ocupado
    'Lq (Clientes en cola)': 0.083,       # promedio esperando
    'Wq (Espera promedio)': 0.1,          # horas
    'Ws (Tiempo total)': 0.6,             # horas
    'total_chats': 12,
    'chats_completados': 10,
    'tiempo_promedio_servicio': 1800.0,   # segundos
    'estado': 'calculado'
}
```

---

## ⚠️ PROBLEMAS COMUNES

| Problema | Solución |
|----------|----------|
| Botón no aparece | Verificar `chat_widget.js` y recargar página |
| Posición no se ve | Revisar base de datos: `Chat.objects.filter(estado='esperando')` |
| Métricas "sin_datos" | Crear chats completados: `Chat.objects.create(...duracion_segundos=600)` |
| Comando no funciona | Crear `chat/management/commands/` con `__init__.py` |

---

## 📦 ARCHIVOS DE DOCUMENTACIÓN

```
chat/
├─ MM1_README.md          ← Documentación técnica completa
├─ START_HERE.txt         ← Guía de inicio rápido
├─ TESTING_GUIDE.txt      ← Cómo probar
├─ DEBUGGING_GUIDE.txt    ← Troubleshooting
├─ ADVANCED_GUIDE.txt     ← Extensiones avanzadas
└─ IMPLEMENTATION_SUMMARY.txt
```

---

## ✨ FUNCIONES PRINCIPALES

### `asignar_prioridad(mensaje)`
```python
"urgente", "reclamo", "problema"  → 3 (urgente)
"pedido", "compra", "orden"       → 2 (importante)
Resto                             → 1 (normal)
```

### `procesar_cola()`
```python
# Actualiza el siguiente chat a 'en_atencion'
siguiente = procesar_cola()
# Retorna: Chat object o None
```

### `chat_personalizado(request)`
```python
POST /chat/personalizado/
{
    "usuario_id": 1,
    "message": "Necesito ayuda"
}
# Retorna: JSON con respuesta y posición en cola
```

### `calcular_metricas(horas_atras=24)`
```python
# Calcula todas las métricas M/M/1
metricas = calcular_metricas(horas_atras=24)
# Retorna: Dict con todas las métricas
```

### `obtener_estadisticas_cola()`
```python
# Estadísticas en TIEMPO REAL
stats = obtener_estadisticas_cola()
# Retorna: Dict con estado actual de la cola
```

---

## 🌐 ENDPOINTS

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/chat/personalizado/` | POST | Solicitar atención personalizada |
| `/chat/widget/` | GET | Cargar widget del chat |
| `/chat/send/` | POST | Enviar mensaje (existente) |

---

## 📊 TABLA DE ESTADOS

| Estado | Significado | Siguiente estado |
|--------|-------------|------------------|
| `esperando` | En cola | `en_atencion` |
| `en_atencion` | Siendo atendido | `finalizado` |
| `finalizado` | Atención completada | - |
| `cancelado` | Cancelado por usuario | - |

---

## 🔐 BASE DE DATOS: Modelo Chat

```sql
-- Campos principales:
id              → ID único
usuario_id      → Referencia a usuario
estado          → 'esperando', 'en_atencion', 'finalizado', 'cancelado'
prioridad       → 1, 2 o 3
llegada         → Cuándo se solicita
inicio_servicio → Cuándo inicia atención
fin_servicio    → Cuándo termina
duracion_segundos → Tiempo total atendido
```

---

## 🧮 EJEMPLO DE CÁLCULO

**Datos reales:** 20 chats en 24 horas, tiempo promedio 10 minutos

```
λ = 20 clientes / 24 horas = 0.83 clientes/hora
μ = 1 / (600 seg / 3600) = 6 clientes/hora
ρ = 0.83 / 6 = 0.138 (13.8% ocupado)

Lq = 0.138² / (1 - 0.138) = 0.022 clientes
Wq = 0.022 / 0.83 = 0.0265 horas ≈ 1.6 minutos
Ws = 1 / (6 - 0.83) = 0.186 horas ≈ 11.1 minutos
```

→ **Sistema muy eficiente: usuarios esperan poco**

---

## 📝 ARCHIVOS MODIFICADOS

```
✅ chat/models.py              - Campos M/M/1 ya existen
✅ chat/views.py               - 3 funciones nuevas agregadas
✅ chat/urls.py                - Ruta /chat/personalizado/
✅ chat/metrics.py             - NUEVO: Cálculos M/M/1
✅ static/js/chat_widget.js    - Botón "Atención Personalizada"
✅ management/commands/        - NUEVO: show_queue_stats.py
```

---

## ✅ VERIFICACIÓN RÁPIDA

```bash
# 1. ¿Funciona el servidor?
python manage.py check
# Esperado: "System check identified no issues"

# 2. ¿Funciona el endpoint?
curl -X POST http://127.0.0.1:8000/chat/personalizado/ \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": 1, "message": "test"}'

# 3. ¿Se crean chats?
python manage.py shell
from chat.models import Chat
Chat.objects.count()

# 4. ¿Se calculan métricas?
from chat.metrics import calcular_metricas
calcular_metricas()

# 5. ¿Funciona el comando?
python manage.py show_queue_stats
```

---

**¡Listo para usar! 🚀**

Para más detalles, lee: `GUIA_COMPLETA_TEORIA_COLAS.md`
