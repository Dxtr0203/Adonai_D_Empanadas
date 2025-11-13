#!/usr/bin/env python
"""
Script de prueba rápida para validar el sistema M/M/1

Para ejecutar desde Django shell:
    python manage.py shell < chat/quick_test.py
    
O simplemente copiar y pegar cada bloque en Django shell:
    python manage.py shell
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from chat.models import Chat, MensajeChat
from usuarios.models import Usuario
from chat.views import asignar_prioridad, procesar_cola
from chat.metrics import calcular_metricas, obtener_estadisticas_cola

print("\n" + "="*80)
print("PRUEBA RÁPIDA DEL SISTEMA M/M/1")
print("="*80)

# Test 1: Verificar modelo Chat
print("\n[TEST 1] Verificar estructura del modelo Chat")
print("-" * 80)
try:
    chat_count = Chat.objects.count()
    print(f"✅ Modelo Chat accesible. Total de chats en BD: {chat_count}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Probar asignación de prioridad
print("\n[TEST 2] Probar asignación de prioridad")
print("-" * 80)
tests_prioridad = [
    ("Necesito atención urgente", 3),
    ("Tengo un reclamo", 3),
    ("Quiero hacer un pedido", 2),
    ("Necesito comprar algo", 2),
    ("Hola", 1),
    ("¿Cuál es tu horario?", 1),
]

for texto, esperado in tests_prioridad:
    resultado = asignar_prioridad(texto)
    status = "✅" if resultado == esperado else "❌"
    print(f"{status} '{texto}' → Prioridad {resultado} (esperado {esperado})")

# Test 3: Obtener usuarios
print("\n[TEST 3] Obtener usuarios disponibles")
print("-" * 80)
try:
    usuarios = Usuario.objects.all()[:3]
    if usuarios.exists():
        for user in usuarios:
            print(f"✅ Usuario: {user.id} - {user.email}")
    else:
        print("⚠️  No hay usuarios en la BD. Las pruebas siguientes necesitarán usuarios.")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Crear un chat de prueba
print("\n[TEST 4] Crear un chat de prueba")
print("-" * 80)
try:
    usuario = Usuario.objects.first()
    if usuario:
        chat_test = Chat.objects.create(
            usuario=usuario,
            estado='esperando',
            prioridad=2,
            llegada=timezone.now() - timedelta(minutes=5)
        )
        print(f"✅ Chat creado: ID={chat_test.id}, Estado={chat_test.estado}, Prioridad={chat_test.prioridad}")
    else:
        print("⚠️  No hay usuarios para crear chat de prueba")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Procesar cola
print("\n[TEST 5] Procesar cola M/M/1")
print("-" * 80)
try:
    siguiente = procesar_cola()
    if siguiente:
        print(f"✅ Chat procesado: ID={siguiente.id}, Estado={siguiente.estado}")
        print(f"   - Inicio de servicio: {siguiente.inicio_servicio}")
    else:
        print("ℹ️  No hay chats esperando en la cola")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 6: Obtener estadísticas
print("\n[TEST 6] Obtener estadísticas de cola")
print("-" * 80)
try:
    stats = obtener_estadisticas_cola()
    print(f"✅ Estadísticas obtenidas:")
    print(f"   - En espera: {stats['en_cola']}")
    print(f"   - En atención: {stats['en_atencion']}")
    print(f"   - Finalizados: {stats['finalizados']}")
    print(f"   - Tiempo espera promedio: {stats['tiempo_espera_promedio_minutos']} min")
    print(f"   - Servidor disponible: {stats['servidor_disponible']}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 7: Calcular métricas M/M/1
print("\n[TEST 7] Calcular métricas M/M/1")
print("-" * 80)
try:
    metricas = calcular_metricas(horas_atras=24)
    print(f"✅ Métricas calculadas:")
    print(f"   - λ (Tasa llegada): {metricas['λ (Tasa llegada)']} clientes/hora")
    print(f"   - μ (Tasa servicio): {metricas['μ (Tasa servicio)']} clientes/hora")
    print(f"   - ρ (Utilización): {metricas['ρ (Utilización)']}")
    print(f"   - Lq (Clientes en cola): {metricas['Lq (Clientes en cola)']}")
    print(f"   - Wq (Espera promedio): {metricas['Wq (Espera promedio)']} horas")
    print(f"   - Ws (Tiempo total): {metricas['Ws (Tiempo total)']} horas")
    print(f"   - Total chats: {metricas['total_chats']}")
    print(f"   - Completados: {metricas['chats_completados']}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 8: Crear mensaje de chat
print("\n[TEST 8] Crear mensaje de chat")
print("-" * 80)
try:
    chat = Chat.objects.filter(estado='esperando').first()
    if chat:
        mensaje = MensajeChat.objects.create(
            chat=chat,
            remitente='Usuario',
            contenido='Necesito atención personalizada'
        )
        print(f"✅ Mensaje creado: ID={mensaje.id}, Chat={chat.id}")
    else:
        print("ℹ️  No hay chats esperando")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 9: Calcular duración
print("\n[TEST 9] Finalizar chat y calcular duración")
print("-" * 80)
try:
    chat = Chat.objects.filter(estado='esperando').first()
    if chat:
        chat.estado = 'finalizado'
        chat.fin_servicio = timezone.now()
        chat.duracion_segundos = int((chat.fin_servicio - chat.inicio_servicio).total_seconds()) if chat.inicio_servicio else 0
        chat.save()
        print(f"✅ Chat finalizado: ID={chat.id}, Duración={chat.duracion_segundos}s")
    else:
        print("ℹ️  No hay chats en espera para finalizar")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 10: Verificar rutas
print("\n[TEST 10] Verificar rutas Django")
print("-" * 80)
try:
    from django.urls import reverse
    url_send = reverse('chat:send')
    url_personalizado = reverse('chat:personalizado')
    print(f"✅ Ruta /chat/send/ → {url_send}")
    print(f"✅ Ruta /chat/personalizado/ → {url_personalizado}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80)
print("PRUEBAS COMPLETADAS")
print("="*80 + "\n")
