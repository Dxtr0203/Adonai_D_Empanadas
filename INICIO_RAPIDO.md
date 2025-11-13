# 🚀 INICIO RÁPIDO: SISTEMA M/M/1

## ⏱️ Tiempo estimado: 10 minutos

---

## PASO 1: Instalar Dependencias (2 minutos)

### En PowerShell:

```powershell
cd "C:\Users\Dxtr\Desktop\Adonai\Adonai_D_Empanadas"

# Instalar MySQLdb para conexión a MySQL
pip install mysqlclient

# Si hay error, intenta con pymysql
pip install pymysql
```

### Si falla MySQLdb, usa SQLite (sin cambios):

```powershell
# Edita adonai/settings.py y cambia:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
```

---

## PASO 2: Preparar la Base de Datos (2 minutos)

```powershell
# Ejecutar migraciones
python manage.py migrate

# Crear superusuario (si no existe)
python manage.py createsuperuser
# Sigue las instrucciones (email: admin@test.com, password: admin123)
```

---

## PASO 3: Iniciar el Servidor (1 minuto)

```powershell
# En la misma carpeta
python manage.py runserver

# Esperado:
# Starting development server at http://127.0.0.1:8000/
# Quit the server with CTRL-BREAK
```

---

## PASO 4: Probar en Navegador (2 minutos)

```
1. Abre: http://127.0.0.1:8000/
2. Inicia sesión (o ve a http://127.0.0.1:8000/usuarios/login/)
3. Haz clic en el chat (esquina inferior derecha)
4. Haz clic en: "Atención Personalizada"
5. ¡Deberías ver tu respuesta en la cola!
```

---

## PASO 5: Ver Estadísticas (2 minutos)

### En otra terminal PowerShell:

```powershell
cd "C:\Users\Dxtr\Desktop\Adonai\Adonai_D_Empanadas"

# Ver métricas del sistema
python manage.py show_queue_stats

# Esperado (algo similar):
# ╔════════════════════════════════════════════════╗
# ║      ESTADÍSTICAS DE COLA M/M/1                ║
# ╚════════════════════════════════════════════════╝
# ...
```

---

## PASO 6: Acceder a Django Shell (opcional, 2 minutos)

```powershell
# Abrir shell interactivo
python manage.py shell

# Una vez dentro (>>>):

# Ver chats actuales
from chat.models import Chat
Chat.objects.count()

# Ver métricas
from chat.metrics import calcular_metricas
print(calcular_metricas())

# Ver estadísticas en tiempo real
from chat.metrics import obtener_estadisticas_cola
print(obtener_estadisticas_cola())

# Salir
exit()
```

---

## ✅ VERIFICACIÓN RÁPIDA

Ejecuta esto para confirmar que todo funciona:

```powershell
# En PowerShell:
cd "C:\Users\Dxtr\Desktop\Adonai\Adonai_D_Empanadas"

# 1. Verificar archivos existen
Test-Path "chat\models.py"      # Should be True
Test-Path "chat\views.py"       # Should be True
Test-Path "chat\metrics.py"     # Should be True
Test-Path "static\js\chat_widget.js"  # Should be True

# 2. Verificar funciones en views.py
Select-String "def chat_personalizado" chat\views.py

# 3. Verificar métricas
Select-String "def calcular_metricas" chat\metrics.py
```

---

## 🎯 CHECKLIST DE FUNCIONAMIENTO

- [ ] MySQLdb instalado sin errores
- [ ] Migraciones ejecutadas exitosamente
- [ ] Servidor inicia sin errores
- [ ] Puedes iniciar sesión en http://127.0.0.1:8000
- [ ] Ves el botón "Atención Personalizada" en el chat
- [ ] Al hacer clic, ves un mensaje de la cola
- [ ] El comando `python manage.py show_queue_stats` funciona
- [ ] `python manage.py shell` muestra métricas

**Si todos están marcados: ✅ SISTEMA FUNCIONAL**

---

## 🐛 SI ALGO FALLA

### Error: "No module named MySQLdb"
```powershell
# Solución 1: Instalar mysqlclient
pip install mysqlclient

# Solución 2: Usar SQLite en lugar de MySQL
# Edita adonai/settings.py
```

### Error: "Connection refused"
```powershell
# Si usas MySQL, verifica que el servidor MySQL esté corriendo:
# 1. Abre Services (servicios de Windows)
# 2. Busca "MySQL"
# 3. Si no está corriendo, inicia el servicio

# O simplemente cambia a SQLite (más fácil para desarrollo)
```

### Error: "Tabla no existe"
```powershell
# Ejecuta migraciones
python manage.py migrate

# Y luego crea datos de prueba
python manage.py shell < chat/quick_test.py
```

### El botón no aparece
```powershell
# 1. Recarga la página (Ctrl+F5)
# 2. Verifica en la consola (F12 → Console) si hay errores JavaScript
# 3. Verifica que chat_widget.js está actualizado
```

---

## 📚 DOCUMENTOS DISPONIBLES

Una vez que funcione, puedes leer (en orden de recomendación):

1. **REFERENCIA_RAPIDA_M_M1.md** (5 min)
   - Referencia rápida de comandos y funciones

2. **GUIA_COMPLETA_TEORIA_COLAS.md** (30 min)
   - Explicación detallada del sistema

3. **DIAGRAMAS_VISUALES_M_M1.md** (15 min)
   - Visualización del flujo y arquitectura

4. **VERIFICACION_SISTEMA_COMPLETO.md** (10 min)
   - Confirmación de que todo está implementado

5. **INDICE_GUIAS_M_M1.md** (5 min)
   - Índice y resumen de todo

---

## 🧪 PRUEBA RÁPIDA (SIN NAVEGADOR)

Si no quieres abrir el navegador, ejecuta:

```powershell
# 1. Abre Django shell
python manage.py shell

# 2. Copia y pega esto:
from django.test import RequestFactory
from django.http import HttpRequest
from chat.views import chat_personalizado
from usuarios.models import Usuario
import json

# Obtener un usuario
try:
    usuario = Usuario.objects.first()
    if not usuario:
        print("No hay usuarios. Crea uno primero.")
    else:
        # Crear request simulado
        factory = RequestFactory()
        request = factory.post(
            '/chat/personalizado/',
            data=json.dumps({'usuario_id': usuario.id, 'message': 'Test urgente'}),
            content_type='application/json'
        )
        
        # Ejecutar vista
        response = chat_personalizado(request)
        
        # Ver respuesta
        print("RESPUESTA:")
        print(response.content.decode())
except Exception as e:
    print(f"Error: {e}")

# 3. Escribir: exit()
exit()
```

---

## ⚡ COMANDO ÚNICO (Si todo está listo)

Si ya tienes todo configurado:

```powershell
# En una terminal:
python manage.py runserver

# En otra terminal:
python manage.py show_queue_stats

# En el navegador:
# http://127.0.0.1:8000
```

---

## 📊 PRÓXIMOS PASOS (Opcional)

Una vez que funciona, puedes:

1. **Integrar con Gemini AI** (ver ADVANCED_GUIDE.txt)
2. **Crear panel administrativo** para ver cola gráficamente
3. **Agregar WebSockets** para notificaciones en tiempo real
4. **Crear reportes** de métricas diarias/semanales

---

## 💡 TIPS

- Si usas **SQLite**, es más fácil para desarrollo: no necesitas servidor MySQL
- El sistema es **completamente funcional** sin cambios adicionales
- Puedes **crear múltiples usuarios** para probar la cola
- Las **métricas se calculan automáticamente** desde los datos en BD

---

## ✅ RESUMEN

```
├─ Instala dependencias
├─ Ejecuta migraciones
├─ Inicia servidor
├─ Abre navegador
├─ Prueba "Atención Personalizada"
└─ ¡Listo! 🎉
```

**Tiempo total: 10 minutos**

---

## 🎓 Si necesitas ayuda

1. **Consulta:** `REFERENCIA_RAPIDA_M_M1.md` (problemas comunes)
2. **Lee:** `chat/DEBUGGING_GUIDE.txt` (troubleshooting detallado)
3. **Revisa:** Código en `chat/views.py` (comentado y claro)

---

**¡Estás listo para empezar! 🚀**

Última actualización: 13 de Noviembre de 2024
