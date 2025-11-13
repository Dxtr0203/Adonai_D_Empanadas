"""
Módulo de métricas para el sistema de colas M/M/1 del chatbot.

Calcula indicadores de rendimiento y eficiencia del servicio de atención personalizada.
"""

from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Chat


def calcular_metricas(horas_atras=24):
    """
    Calcula métricas M/M/1 basadas en los chats completados recientemente.
    
    Args:
        horas_atras: Número de horas en el pasado para considerar (default: 24)
    
    Returns:
        dict: Diccionario con métricas calculadas
    """
    # Filtrar chats de las últimas N horas
    tiempo_limite = timezone.now() - timedelta(hours=horas_atras)
    chats_recientes = Chat.objects.filter(
        llegada__gte=tiempo_limite
    )
    
    # Chats completados con duración registrada
    chats_completados = chats_recientes.filter(
        estado='finalizado',
        duracion_segundos__isnull=False
    )
    
    total_chats = chats_recientes.count()
    total_completados = chats_completados.count()
    
    # Si no hay datos, retornar valores por defecto
    if total_completados == 0:
        return {
            'λ (Tasa llegada)': 0,
            'μ (Tasa servicio)': 0,
            'ρ (Utilización)': 0,
            'Lq (Clientes en cola)': 0,
            'Wq (Espera promedio)': 0,
            'Ws (Tiempo total)': 0,
            'total_chats': total_chats,
            'chats_completados': total_completados,
            'tiempo_promedio_servicio': 0,
            'estado': 'sin_datos'
        }
    
    # Calcular tiempo promedio de servicio (en segundos)
    tiempo_promedio_servicio = chats_completados.aggregate(
        promedio=Avg('duracion_segundos')
    )['promedio'] or 1
    
    # Convertir a horas para los cálculos
    tiempo_promedio_servicio_horas = tiempo_promedio_servicio / 3600
    
    # Tasa de llegada (λ) = total de llegadas / horas
    tasa_llegada = total_chats / horas_atras if horas_atras > 0 else 0
    
    # Tasa de servicio (μ) = 1 / tiempo promedio servicio (en horas)
    tasa_servicio = 1 / tiempo_promedio_servicio_horas if tiempo_promedio_servicio_horas > 0 else 0
    
    # Factor de utilización (ρ) = λ / μ
    rho = tasa_llegada / tasa_servicio if tasa_servicio > 0 else 0
    
    # Limitar rho a 0.99 para evitar inestabilidad (ρ debe ser < 1)
    if rho >= 1:
        rho = 0.99
    
    # Cálculos M/M/1
    # Lq = ρ² / (1 - ρ)  [Número promedio de clientes en cola]
    Lq = (rho ** 2) / (1 - rho) if (1 - rho) > 0 else 0
    
    # Wq = Lq / λ  [Tiempo promedio en cola]
    Wq = Lq / tasa_llegada if tasa_llegada > 0 else 0
    
    # Ws = 1 / (μ - λ)  [Tiempo promedio total en el sistema]
    Ws = 1 / (tasa_servicio - tasa_llegada) if (tasa_servicio - tasa_llegada) > 0 else 0
    
    return {
        'λ (Tasa llegada)': round(tasa_llegada, 4),
        'μ (Tasa servicio)': round(tasa_servicio, 4),
        'ρ (Utilización)': round(rho, 3),
        'Lq (Clientes en cola)': round(Lq, 3),
        'Wq (Espera promedio)': round(Wq, 3),
        'Ws (Tiempo total)': round(Ws, 3),
        'total_chats': total_chats,
        'chats_completados': total_completados,
        'tiempo_promedio_servicio': round(tiempo_promedio_servicio, 2),
        'estado': 'calculado'
    }


def obtener_estadisticas_cola():
    """
    Obtiene estadísticas en tiempo real de la cola actual.
    
    Returns:
        dict: Estadísticas de la cola
    """
    chats_esperando = Chat.objects.filter(estado='esperando').count()
    chats_en_atencion = Chat.objects.filter(estado='en_atencion').count()
    chats_finalizados = Chat.objects.filter(estado='finalizado').count()
    
    # Tiempo promedio de espera de los que están esperando
    chats_esperando_qs = Chat.objects.filter(estado='esperando')
    tiempo_espera_promedio = 0
    
    if chats_esperando_qs.exists():
        ahora = timezone.now()
        tiempos_espera = []
        for chat in chats_esperando_qs:
            tiempo_espera = (ahora - chat.llegada).total_seconds() / 60  # en minutos
            tiempos_espera.append(tiempo_espera)
        tiempo_espera_promedio = sum(tiempos_espera) / len(tiempos_espera) if tiempos_espera else 0
    
    return {
        'en_cola': chats_esperando,
        'en_atencion': chats_en_atencion,
        'finalizados': chats_finalizados,
        'tiempo_espera_promedio_minutos': round(tiempo_espera_promedio, 2),
        'servidor_disponible': chats_en_atencion == 0
    }


def obtener_resumen_metricas():
    """
    Obtiene un resumen completo de métricas y estadísticas de la cola.
    
    Returns:
        dict: Resumen general de métricas
    """
    metricas_mm1 = calcular_metricas(horas_atras=24)
    estadisticas_cola = obtener_estadisticas_cola()
    
    resumen = {
        'metricas_mm1': metricas_mm1,
        'estadisticas_cola_actual': estadisticas_cola,
        'timestamp': timezone.now().isoformat()
    }
    
    return resumen
