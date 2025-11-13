# 📚 GUÍA COMPLETA: SISTEMA DE TEORÍA DE COLAS M/M/1
## Adonai Store Chatbot - Sistema de Atención Personalizada

---

## 📍 LOCALIZACIÓN DE ARCHIVOS

Tu código de Teoría de Colas está completamente ubicado en la carpeta `chat/`:

```
chat/
├── models.py                          ← Modelo Chat con campos M/M/1
├── views.py                           ← Lógica de atención (líneas 343-420+)
├── urls.py                            ← Ruta /chat/personalizado/
├── metrics.py                         ← Cálculos de métricas M/M/1 ⭐
├── management/
│   └── commands/
│       └── show_queue_stats.py        ← Comando para ver estadísticas
├── MM1_README.md                      ← Documentación técnica
├── START_HERE.txt                     ← Guía de inicio rápido
├── TESTING_GUIDE.txt                  ← Cómo probar el sistema
├── DEBUGGING_GUIDE.txt                ← Troubleshooting
├── ADVANCED_GUIDE.txt                 ← Extensiones avanzadas
└── quick_test.py                      ← Script de prueba automática

static/js/
└── chat_widget.js                     ← Frontend del botón "Atención Personalizada"
```

---

## 🎯 ¿QUÉ ES EL SISTEMA M/M/1?

### Definición
**M/M/1** es un modelo matemático de **Teoría de Colas** que simula:
- Un **servidor único** atendiendo clientes
- **Llegadas aleatorias** (distribución de Poisson)
- **Tiempos de servicio aleatorios** (distribución exponencial)

### Parámetros Principales

| Parámetro | Símbolo | Significado | Ejemplo |
|-----------|---------|-------------|---------|
| Tasa de llegada | λ (lambda) | Clientes que llegan por hora | 5 clientes/hora |
| Tasa de servicio | μ (mu) | Clientes atendidos por hora | 10 clientes/hora |
| Utilización | ρ (rho) | % de tiempo que el servidor está ocupado | 0.5 (50%) |
| Clientes en cola | Lq | Promedio de clientes esperando | 0.33 clientes |
| Tiempo en cola | Wq | Tiempo promedio de espera | 0.067 horas (4 min) |
| Tiempo total | Ws | Tiempo promedio en el sistema | 0.2 horas (12 min) |

### Fórmulas M/M/1

```
λ = Total de clientes / Horas
μ = 1 / Tiempo promedio de servicio (en horas)
ρ = λ / μ

Lq = ρ² / (1 - ρ)
Wq = Lq / λ
Ws = 1 / (μ - λ)
```

**Condición de estabilidad:** ρ < 1 (Si ρ ≥ 1, la cola crece infinitamente)

---

## 🔧 COMPONENTES DEL SISTEMA

### 1. **Modelo de Base de Datos** (`models.py`)

```python
class Chat(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    
    # Estados del ciclo de vida
    estado = models.CharField(
        choices=[
            ('esperando', 'esperando'),      # En la cola esperando
            ('en_atencion', 'en_atencion'),  # Siendo atendido
            ('finalizado', 'finalizado'),    # Atención completada
            ('cancelado', 'cancelado')       # Cancelado por el usuario
        ]
    )
    
    # Prioridad (1=normal, 2=importante, 3=urgente)
    prioridad = models.IntegerField(default=1)
    
    # Timestamps
    llegada = models.DateTimeField(auto_now_add=True)          # Cuándo se solicita
    inicio_servicio = models.DateTimeField(null=True)          # Cuándo inicia atención
    fin_servicio = models.DateTimeField(null=True)             # Cuándo termina
    duracion_segundos = models.IntegerField(null=True)         # Tiempo total atendido
```

**Modelo complementario:**
```python
class MensajeChat(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    remitente = ('Usuario', 'Bot', 'Empleado')
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
```

---

### 2. **Lógica de Atención** (`views.py`)

#### Función `asignar_prioridad(mensaje)`
Asigna automáticamente prioridad según palabras clave:

```python
Palabras clave urgentes ("urgente", "reclamo", "problema")    → Prioridad 3
Palabras clave importantes ("pedido", "compra", "orden")       → Prioridad 2
Resto de mensajes                                              → Prioridad 1
```

#### Función `procesar_cola()`
Gestiona qué usuario es atendido:

```
¿Hay alguien en 'en_atencion'?
    ├─ SÍ  → No hacer nada (esperar a que termine)
    └─ NO  → Obtener el primer 'esperando' (ordenado por prioridad y llegada)
             Cambiar estado a 'en_atencion'
             Registrar inicio_servicio
```

#### Endpoint `POST /chat/personalizado/`

**Request:**
```json
{
    "usuario_id": 1,
    "message": "Tengo un problema urgente con mi pedido"
}
```

**Response:**
```json
{
    "ok": true,
    "reply": "📋 Has sido agregado a la cola de atención personalizada.\nHay 2 cliente(s) antes que tú. Tu turno llegará pronto.",
    "posicion": 3,
    "estado": "esperando",
    "chat_id": 123,
    "suggested": []
}
```

---

### 3. **Cálculo de Métricas** (`metrics.py`)

#### Función `calcular_metricas(horas_atras=24)`

Calcula todas las métricas M/M/1 basadas en datos históricos:

```python
from chat.metrics import calcular_metricas

metricas = calcular_metricas(horas_atras=24)

# Retorna:
{
    'λ (Tasa llegada)': 0.5,              # clientes/hora
    'μ (Tasa servicio)': 2.0,             # clientes/hora
    'ρ (Utilización)': 0.25,              # 25% ocupado
    'Lq (Clientes en cola)': 0.083,       # promedio esperando
    'Wq (Espera promedio)': 0.1,          # horas = 6 minutos
    'Ws (Tiempo total)': 0.6,             # horas = 36 minutos
    'total_chats': 12,                    # chats en las 24h
    'chats_completados': 10,              # chats terminados
    'tiempo_promedio_servicio': 1800.0,   # 30 minutos en segundos
    'estado': 'calculado'
}
```

#### Función `obtener_estadisticas_cola()`

Estadísticas **en tiempo real** de la cola actual:

```python
from chat.metrics import obtener_estadisticas_cola

stats = obtener_estadisticas_cola()

# Retorna:
{
    'en_cola': 3,                         # Usuarios esperando ahora
    'en_atencion': 1,                     # Usuarios siendo atendidos
    'finalizados': 15,                    # Total completados
    'tiempo_espera_promedio_minutos': 4.5,
    'servidor_disponible': False          # ¿Hay servidor libre?
}
```

---

## 📊 FLUJO COMPLETO DE FUNCIONAMIENTO

### Escenario: Usuario solicita "Atención Personalizada"

```
PASO 1: Usuario hace clic en "Atención Personalizada"
│
├─ JavaScript (frontend) envía POST a /chat/personalizado/
│  {usuario_id: 1, message: "Tengo un problema"}
│
PASO 2: Backend recibe y procesa
│
├─ chat_personalizado(request):
│  1. Valida usuario
│  2. Asigna prioridad = asignar_prioridad("Tengo un problema") = 3
│  3. Crea Chat(usuario=1, estado='esperando', prioridad=3)
│  4. Guarda MensajeChat(remitente='Usuario', contenido=...)
│
PASO 3: Procesar la cola
│
├─ procesar_cola():
│  1. Busca si hay Chat en 'en_atencion'
│  2. Si NO hay: Toma el primer 'esperando' (ordenado por prioridad DESC, llegada ASC)
│     - Cambia estado a 'en_atencion'
│     - Registra inicio_servicio = now()
│  3. Si SÍ hay: No hace nada
│
PASO 4: Determinar respuesta
│
├─ Si el chat fue pasado a 'en_atencion':
│  "🎧 ¡Tu turno ha llegado! Iniciando atención personalizada..."
│  posicion = 0
│
├─ Si sigue en 'esperando':
│  Calcula posicion = count(chats esperando ANTES de este)
│  "📋 Has sido agregado a la cola. Hay X cliente(s) antes que tú."
│  posicion = X + 1
│
PASO 5: Guardar respuesta del Bot
│
├─ MensajeChat(remitente='Bot', contenido=reply)
│
PASO 6: Retornar JSON
│
└─ return JsonResponse({...})
```

### Ejemplo con Múltiples Usuarios

```
MOMENTO 1 (10:00)
├─ Usuario Juan solicita atención
├─ procesar_cola() → No hay en 'en_atencion'
├─ Juan → 'en_atencion' (Inicio: 10:00)
├─ Respuesta: "¡Tu turno ha llegado!"

MOMENTO 2 (10:05)
├─ Usuario María solicita atención
├─ procesar_cola() → Juan está en 'en_atencion'
├─ María → 'esperando' (Prioridad 2)
├─ Respuesta: "Hay 0 clientes antes que tú. ¡Eres siguiente!"

MOMENTO 3 (10:07)
├─ Usuario Carlos solicita atención (URGENTE - Prioridad 3)
├─ procesar_cola() → Juan sigue en 'en_atencion'
├─ Carlos → 'esperando' (Prioridad 3 - más urgente que María)
├─ Respuesta: "Hay 1 cliente antes que tú."

MOMENTO 4 (10:12) 
├─ Juan finaliza atención (duracion = 720 segundos = 12 min)
├─ procesar_cola() → ¿Quién atender?
│  1. Busca esperando ordenados por prioridad DESC, llegada ASC
│  2. Carlos (Prioridad 3, llegada 10:07) es el primero
├─ Carlos → 'en_atencion' (Inicio: 10:12)
├─ María sigue esperando

MOMENTO 5 (10:25)
├─ Carlos finaliza atención
├─ procesar_cola() → María es la única esperando
├─ María → 'en_atencion' (Inicio: 10:25)
```

---

## 🧪 CÓMO PROBAR EL SISTEMA (FUNCIONAL)

### Opción 1: Desde el Navegador ✅

```bash
# 1. Iniciar servidor
python manage.py runserver

# 2. Abrir en navegador
http://127.0.0.1:8000

# 3. Inicia sesión
# 4. Haz clic en el chat (esquina inferior derecha)
# 5. Haz clic en "Atención Personalizada"
# 6. Recibirás un mensaje indicando tu posición en la cola
```

### Opción 2: Desde Django Shell ✅

```bash
# Acceder a shell
python manage.py shell

# Importar lo necesario
from chat.models import Chat, MensajeChat
from chat.views import chat_personalizado, procesar_cola
from chat.metrics import calcular_metricas, obtener_estadisticas_cola
from usuarios.models import Usuario
from django.utils import timezone
from django.test import RequestFactory
import json

# Test 1: Ver usuarios disponibles
usuarios = Usuario.objects.all()
print(f"Usuarios disponibles: {[u.email for u in usuarios]}")

# Test 2: Crear un "request" simulado
factory = RequestFactory()
usuario = Usuario.objects.first()

request = factory.post('/chat/personalizado/', 
    data=json.dumps({'usuario_id': usuario.id, 'message': 'Tengo un problema urgente'}),
    content_type='application/json'
)

# Test 3: Ejecutar la función
response = chat_personalizado(request)
print(response.content)

# Test 4: Ver la cola actual
chats_esperando = Chat.objects.filter(estado='esperando').order_by('llegada')
print(f"En cola: {chats_esperando.count()} usuarios")

# Test 5: Ver estadísticas
stats = obtener_estadisticas_cola()
print(f"Estadísticas: {stats}")

# Test 6: Ver métricas M/M/1
metricas = calcular_metricas(horas_atras=24)
print(f"Métricas: {metricas}")
```

### Opción 3: Desde Terminal (Comando) ✅

```bash
# Ver estadísticas actuales
python manage.py show_queue_stats

# Salida esperada:
# ╔════════════════════════════════════════════════╗
# ║      ESTADÍSTICAS DE COLA M/M/1                ║
# ╚════════════════════════════════════════════════╝
# 
# Tasa de llegada (λ):        0.5000
# Tasa de servicio (μ):       2.0000
# Utilización (ρ):            0.2500
# Clientes en cola (Lq):      0.0833
# Tiempo en cola (Wq):        0.1000 horas
# Tiempo total (Ws):          0.6000 horas
# ...

# Con opciones
python manage.py show_queue_stats --horas 48
python manage.py show_queue_stats --cola
```

### Opción 4: Script de Prueba Automática ✅

```bash
# Ejecutar pruebas automáticas
python manage.py shell < chat/quick_test.py

# Te mostrará 10 pruebas automáticas
```

---

## 📈 EJEMPLO REAL: ANÁLISIS DE DATOS

Supongamos que en las últimas 24 horas tienes estos datos:

| ID | Usuario | Llegada | Inicio | Fin | Duración |
|----|---------|---------|--------|-----|----------|
| 1 | juan | 10:00 | 10:00 | 10:15 | 900s |
| 2 | maria | 10:05 | 10:15 | 10:30 | 900s |
| 3 | carlos | 10:10 | 10:30 | 10:42 | 720s |
| ... | ... | ... | ... | ... | ... |
| 24 | ana | 18:00 | 18:00 | 18:05 | 300s |

**Cálculos:**
```
Total usuarios: 24
Usuarios completados: 22
Horas: 24

λ = 24 / 24 = 1 cliente/hora
μ = 1 / (13500/22) ≈ 5.87 clientes/hora
ρ = 1 / 5.87 ≈ 0.17 (servidor 17% ocupado)

Lq = 0.17² / (1 - 0.17) ≈ 0.0035 clientes
Wq = 0.0035 / 1 ≈ 0.0035 horas ≈ 12.6 segundos
Ws = 1 / (5.87 - 1) ≈ 0.205 horas ≈ 12.3 minutos
```

**Interpretación:**
- El servidor está muy poco utilizado (17%)
- Los usuarios esperan en promedio 12.6 segundos
- El tiempo total en el sistema es 12.3 minutos
- El sistema es muy eficiente

---

## 🔍 DEBUGGING: PROBLEMAS Y SOLUCIONES

### ❌ El botón "Atención Personalizada" no aparece

**Solución:**
```bash
# 1. Verificar que el archivo chat_widget.js está actualizado
grep -n "Atención Personalizada" static/js/chat_widget.js

# 2. Si no aparece, revisar en la consola de navegador (F12)
# 3. Verificar que las URLs estén cargadas correctamente
```

### ❌ El usuario no ve su posición en la cola

**Solución:**
```python
# En Django shell:
from chat.models import Chat
from django.db.models import Count

# Ver todos los chats esperando
esperando = Chat.objects.filter(estado='esperando').order_by('llegada')
print(f"Usuarios esperando: {esperando.count()}")

# Ver orden de la cola
for i, chat in enumerate(esperando, 1):
    print(f"{i}. {chat.usuario.email} (prioridad {chat.prioridad})")
```

### ❌ Las métricas son incorrectas o muestran "sin_datos"

**Solución:**
```python
# En Django shell:
from chat.models import Chat
from django.utils import timezone
from datetime import timedelta

# Verificar que hay chats completados
tiempo_limite = timezone.now() - timedelta(hours=24)
completados = Chat.objects.filter(
    estado='finalizado',
    duracion_segundos__isnull=False,
    llegada__gte=tiempo_limite
)
print(f"Chats completados en 24h: {completados.count()}")

# Si es 0, crear chats de prueba
from usuarios.models import Usuario
usuario = Usuario.objects.first()
chat = Chat.objects.create(usuario=usuario, estado='finalizado', duracion_segundos=600)
```

### ❌ El comando `show_queue_stats` no funciona

**Solución:**
```bash
# Verificar que el archivo existe
ls -la chat/management/commands/show_queue_stats.py

# Si no existe, crear el archivo o crear la carpeta
mkdir -p chat/management/commands
touch chat/management/commands/__init__.py

# Intentar nuevamente
python manage.py show_queue_stats
```

---

## 💡 CASOS DE USO Y EJEMPLOS

### Caso 1: Tienda con Mucho Tráfico

```
Escenario: Black Friday - 100 clientes por hora

λ = 100 clientes/hora
μ = 10 clientes/hora (pueden atender 1 cada 6 minutos)
ρ = 100 / 10 = 10 ❌ INESTABLE (ρ > 1)

Solución: Aumentar μ a 200+ clientes/hora
- Agregar más servidores (cambiar a M/M/2, M/M/3, etc.)
- Mejorar tiempo de servicio
```

### Caso 2: Tienda Pequeña con Bajo Tráfico

```
Escenario: Tienda pequeña - 2 clientes por hora

λ = 2 clientes/hora
μ = 6 clientes/hora
ρ = 2/6 ≈ 0.33
Lq = 0.33² / (1 - 0.33) ≈ 0.16 clientes
Wq = 0.16 / 2 ≈ 0.08 horas ≈ 4.8 minutos

Interpretación: Sistema muy eficiente, pocas colas
```

---

## 📦 ESTRUCTURA RESUMIDA

```
chat/
│
├─ DATABASE LAYER
│  └─ models.py (Chat, MensajeChat)
│
├─ BUSINESS LOGIC
│  ├─ views.py (asignar_prioridad, procesar_cola, chat_personalizado)
│  └─ metrics.py (calcular_metricas, obtener_estadisticas_cola)
│
├─ API ENDPOINTS
│  └─ urls.py (/chat/personalizado/)
│
├─ FRONTEND
│  └─ templates/chat/ (plantillas)
│
├─ COMMANDS
│  └─ management/commands/show_queue_stats.py
│
└─ DOCUMENTATION
   ├─ MM1_README.md (esta guía)
   ├─ START_HERE.txt
   ├─ TESTING_GUIDE.txt
   ├─ DEBUGGING_GUIDE.txt
   ├─ ADVANCED_GUIDE.txt
   └─ quick_test.py
```

---

## ✅ CHECKLIST: SISTEMA FUNCIONAL

- [x] Modelo Chat creado con campos necesarios
- [x] Función asignar_prioridad() implementada
- [x] Función procesar_cola() implementada
- [x] Endpoint /chat/personalizado/ funcional
- [x] Métricas M/M/1 calculadas correctamente
- [x] Botón "Atención Personalizada" en frontend
- [x] Comando show_queue_stats implementado
- [x] Documentación completa
- [x] Sistema listo para producción

---

## 🎓 RECURSOS ADICIONALES

### Teoría de Colas M/M/1
- Libro: "Operations Research: An Introduction" de Hamdy Taha
- Teoría: https://en.wikipedia.org/wiki/M/M/1_queue
- Fórmulas: https://www.britannica.com/technology/queue

### Implementación en Django
- Django Models: https://docs.djangoproject.com/en/stable/topics/db/models/
- Django Views: https://docs.djangoproject.com/en/stable/topics/http/views/
- Django Shell: https://docs.djangoproject.com/en/stable/ref/django-admin/#shell

### Archivos de Referencia en el Proyecto
- `chat/MM1_README.md` - Documentación técnica
- `chat/TESTING_GUIDE.txt` - Guía de pruebas
- `chat/ADVANCED_GUIDE.txt` - Extensiones avanzadas
- `chat/quick_test.py` - Script de prueba

---

## 🚀 PRÓXIMOS PASOS

1. **Prueba en navegador:**
   ```bash
   python manage.py runserver
   # Abre http://127.0.0.1:8000 e inicia sesión
   ```

2. **Verifica las métricas:**
   ```bash
   python manage.py show_queue_stats
   ```

3. **Integra con tu dashboard (opcional):**
   - Agregaaún template HTML para ver estadísticas
   - Agrega gráficos con Chart.js
   - Crea un endpoint de API para métricas en JSON

4. **Extiende el sistema (opcional):**
   - Ver `ADVANCED_GUIDE.txt` para integración con Gemini AI
   - Agregar WebSockets para notificaciones en tiempo real
   - Crear panel administrativo visual

---

**¡Tu sistema de Teoría de Colas M/M/1 está completamente funcional y listo para usar!** 🎉

Para cualquier duda o problema, consulta los archivos de documentación en `chat/` o contacta al equipo de desarrollo.

Última actualización: 13 de Noviembre de 2024
