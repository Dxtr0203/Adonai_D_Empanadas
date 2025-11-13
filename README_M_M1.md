># 📚 SISTEMA DE TEORÍA DE COLAS M/M/1 - ADONAI STORE

## 🎯 ¿QUÉ ES ESTO?

Tu **sistema completo de Teoría de Colas M/M/1** integrado en el chatbot de Adonai Store.

Permite a los usuarios solicitar **"Atención Personalizada"** y el sistema automáticamente:
- Los añade a una **cola FIFO con prioridades**
- Los atiende cuando hay espacio disponible
- Calcula **métricas matemáticas** en tiempo real (λ, μ, ρ, Lq, Wq, Ws)
- Muestra su **posición en la cola**

**Status:** ✅ **100% FUNCIONAL Y LISTO PARA USAR**

---

## 📂 ¿DÓNDE ESTÁ?

Carpeta: **`chat/`**

### Archivos principales:
```
chat/
├─ models.py          → Modelo Chat con campos M/M/1
├─ views.py           → Lógica principal (procesar_cola, chat_personalizado)
├─ metrics.py         → Cálculos de métricas M/M/1
├─ urls.py            → Endpoint /chat/personalizado/
└─ management/commands/show_queue_stats.py → Comando para ver estadísticas
```

---

## 🚀 EMPEZAR EN 10 MINUTOS

### ⏱️ Opción 1: Inicio Rápido (10 min)

```bash
# 1. Lee esta guía
# 2. Instala dependencias
pip install mysqlclient

# 3. Ejecuta migraciones
python manage.py migrate

# 4. Inicia servidor
python manage.py runserver

# 5. En navegador: http://127.0.0.1:8000
# 6. Inicia sesión → Chat → "Atención Personalizada"
```

**Ver:** `INICIO_RAPIDO.md` para pasos detallados

---

### 📖 Opción 2: Entender el Sistema (30 min)

```
Elige UNA guía:

1. REFERENCIA_RAPIDA_M_M1.md
   → Referencia rápida (5 min)
   
2. GUIA_COMPLETA_TEORIA_COLAS.md
   → Guía completa y detallada (30 min)
   
3. DIAGRAMAS_VISUALES_M_M1.md
   → Visualización con diagramas (15 min)
   
4. VERIFICACION_SISTEMA_COMPLETO.md
   → Confirmación que todo funciona (10 min)
```

---

## 🎯 FLUJO DE FUNCIONAMIENTO

```
Usuario hace clic: "Atención Personalizada"
            ↓
Backend crea Chat(estado='esperando', prioridad=automática)
            ↓
¿Hay servidor libre?
    ├─ SÍ → Chat → 'en_atencion' 
    │       "¡Tu turno ha llegado!"
    │
    └─ NO → Chat → 'esperando'
            "Eres número X en la cola"
            ↓
    Cuando alguien termina:
    procesar_cola() pasa siguiente a 'en_atencion'
```

---

## 🧮 MÉTRICAS CALCULADAS

El sistema calcula automáticamente:

| Métrica | Símbolo | Significado |
|---------|---------|-------------|
| Tasa de llegada | λ | Clientes que llegan por hora |
| Tasa de servicio | μ | Clientes atendidos por hora |
| Utilización | ρ | % de tiempo que el servidor está ocupado |
| Clientes en cola | Lq | Promedio esperando en la cola |
| Tiempo en cola | Wq | Tiempo promedio de espera |
| Tiempo total | Ws | Tiempo promedio en el sistema |

### Ejemplo:
```
λ = 2 clientes/hora
μ = 8 clientes/hora
ρ = 0.25 (servidor 25% ocupado)
Lq = 0.083 (< 1 persona esperando)
Wq = 0.0415 horas (2.5 minutos)
Ws = 0.167 horas (10 minutos)

→ Sistema muy eficiente, sin colas
```

---

## 📊 VER ESTADÍSTICAS

```bash
# Comando para ver métricas en terminal
python manage.py show_queue_stats

# O desde Django shell
python manage.py shell

# Dentro del shell:
from chat.metrics import calcular_metricas, obtener_estadisticas_cola

# Métricas históricas
print(calcular_metricas(horas_atras=24))

# Estado en tiempo real
print(obtener_estadisticas_cola())
```

---

## ✨ CARACTERÍSTICAS

✅ **Atención personalizada con un clic**
- Nuevo botón "Atención Personalizada" en opciones del chat

✅ **Cola FIFO con prioridades**
- Urgencias se atienden primero basado en palabras clave

✅ **Cálculos M/M/1 automáticos**
- Todas las métricas se calculan en tiempo real

✅ **API JSON**
- Endpoint `POST /chat/personalizado/` para integración

✅ **Comando administrativo**
- `python manage.py show_queue_stats`

✅ **Completamente documentado**
- 4 nuevas guías + 8 existentes

---

## 🏗️ ARQUITECTURA

```
FRONTEND (Browser)
    ↓
Chat Widget (JavaScript)
    ↓ POST /chat/personalizado/
BACKEND (Django)
    ↓
chat_personalizado(request) → procesar_cola() → calcular_metricas()
    ↓
DATABASE (MySQL/SQLite)
    ↓
RESPUESTA (JSON)
    ↓
Frontend muestra posición en cola
```

---

## 📋 CHECKLIST: ¿ESTÁ COMPLETO?

- [x] Modelo Chat implementado
- [x] Función asignar_prioridad() implementada
- [x] Función procesar_cola() implementada
- [x] Función chat_personalizado() implementada
- [x] Métricas M/M/1 calculadas
- [x] Estadísticas en tiempo real
- [x] Endpoint API funcional
- [x] Frontend integrado
- [x] Comando admin implementado
- [x] Documentación completa

**RESULTADO: ✅ 100% FUNCIONAL**

---

## 🧪 PROBAR EL SISTEMA

### Opción 1: Navegador
```
1. Inicia servidor: python manage.py runserver
2. Abre: http://127.0.0.1:8000
3. Inicia sesión
4. Chat → "Atención Personalizada"
```

### Opción 2: Django Shell
```python
from chat.metrics import calcular_metricas
print(calcular_metricas(horas_atras=24))
```

### Opción 3: Comando Admin
```bash
python manage.py show_queue_stats
```

---

## 📚 GUÍAS DISPONIBLES

| Documento | Tiempo | Contenido |
|-----------|--------|----------|
| **INICIO_RAPIDO.md** | 10 min | Pasos para empezar |
| **REFERENCIA_RAPIDA_M_M1.md** | 5 min | Referencia rápida |
| **GUIA_COMPLETA_TEORIA_COLAS.md** | 30 min | Guía detallada |
| **DIAGRAMAS_VISUALES_M_M1.md** | 15 min | Visualización |
| **VERIFICACION_SISTEMA_COMPLETO.md** | 10 min | Checklist |
| **INDICE_GUIAS_M_M1.md** | 5 min | Índice completo |

**Documentación en `chat/`:**
- `MM1_README.md` - Técnica
- `START_HERE.txt` - Inicio
- `TESTING_GUIDE.txt` - Testing
- `DEBUGGING_GUIDE.txt` - Debugging
- `ADVANCED_GUIDE.txt` - Avanzado

---

## 🐛 TROUBLESHOOTING

### El botón no aparece
```bash
# Recarga la página (Ctrl+F5)
# Verifica: static/js/chat_widget.js está actualizado
```

### Error "MySQLdb not found"
```bash
pip install mysqlclient
# O usa SQLite en settings.py
```

### Las métricas no se calculan
```bash
# Necesitas datos: crea algunos chats o:
python manage.py shell < chat/quick_test.py
```

### Ver más ayuda:
→ `REFERENCIA_RAPIDA_M_M1.md` (Sección: Problemas Comunes)

---

## 💡 PRÓXIMOS PASOS (Opcional)

1. **Leer una guía** (elige tu preferencia arriba)
2. **Instalar dependencias** y probar en navegador
3. **Ver métricas** con `show_queue_stats`
4. **Explorar código** comentado en `chat/views.py`
5. **Extender sistema** (ver `chat/ADVANCED_GUIDE.txt`)

---

## 🎓 PARA APRENDER MÁS

- **Teoría de Colas:** https://en.wikipedia.org/wiki/M/M/1_queue
- **Django Docs:** https://docs.djangoproject.com/
- **Libro:** "Operations Research: An Introduction" de Hamdy Taha

---

## 📞 ¿NECESITAS AYUDA?

1. **Primer paso:** Lee `REFERENCIA_RAPIDA_M_M1.md`
2. **Si no funciona:** Ve a `chat/DEBUGGING_GUIDE.txt`
3. **Para entender:** Lee `GUIA_COMPLETA_TEORIA_COLAS.md`
4. **Visual:** Ver `DIAGRAMAS_VISUALES_M_M1.md`
5. **Confirmación:** `VERIFICACION_SISTEMA_COMPLETO.md`

---

## 📊 RESUMEN RÁPIDO

```
¿Qué es?       → Sistema de colas M/M/1 para atención personalizada
¿Dónde está?   → Carpeta chat/
¿Funciona?     → ✅ Sí, 100% funcional
¿Está doc.?    → ✅ Sí, 4 nuevas guías + 8 existentes
¿Puedo usarlo? → ✅ Sí, en 10 minutos está funcionando
```

---

## ✅ ESTADO FINAL

| Aspecto | Status |
|---------|--------|
| Código | ✅ Implementado |
| Funcionalidad | ✅ Completa |
| Documentación | ✅ Exhaustiva |
| Testing | ✅ Incluido |
| Producción | ✅ Listo |

**CONCLUSIÓN: SISTEMA COMPLETAMENTE FUNCIONAL** 🎉

---

## 📍 GUÍA DE LECTURA RECOMENDADA

```
Si tienes 10 minutos:     → INICIO_RAPIDO.md
Si tienes 5 minutos:      → REFERENCIA_RAPIDA_M_M1.md
Si tienes 30 minutos:     → GUIA_COMPLETA_TEORIA_COLAS.md
Si quieres visualizar:    → DIAGRAMAS_VISUALES_M_M1.md
Si necesitas todo:        → INDICE_GUIAS_M_M1.md
```

---

**¡Tu sistema de Teoría de Colas está listo para usar! 🚀**

Última actualización: 13 de Noviembre de 2024

---

## 🔗 ESTRUCTURA DE ARCHIVOS

```
Adonai_D_Empanadas/
│
├─ 📘 GUÍAS NUEVAS (creadas para ti)
│  ├─ README.md (este archivo)
│  ├─ INICIO_RAPIDO.md
│  ├─ REFERENCIA_RAPIDA_M_M1.md
│  ├─ GUIA_COMPLETA_TEORIA_COLAS.md
│  ├─ DIAGRAMAS_VISUALES_M_M1.md
│  ├─ VERIFICACION_SISTEMA_COMPLETO.md
│  └─ INDICE_GUIAS_M_M1.md
│
├─ chat/ (Sistema M/M/1)
│  ├─ models.py ✅
│  ├─ views.py ✅
│  ├─ metrics.py ✅
│  └─ management/commands/show_queue_stats.py ✅
│
└─ ... (resto del proyecto)
```

**¡Comienza con: `INICIO_RAPIDO.md`**
