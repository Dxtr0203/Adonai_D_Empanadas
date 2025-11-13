"""
Comando de administración para ver estadísticas de la cola M/M/1
"""

from django.core.management.base import BaseCommand
from chat.metrics import calcular_metricas, obtener_estadisticas_cola, obtener_resumen_metricas


class Command(BaseCommand):
    help = 'Muestra estadísticas y métricas M/M/1 del sistema de colas del chatbot'

    def add_arguments(self, parser):
        parser.add_argument(
            '--horas',
            type=int,
            default=24,
            help='Número de horas en el pasado para considerar (default: 24)'
        )
        parser.add_argument(
            '--cola',
            action='store_true',
            help='Mostrar solo estadísticas de la cola actual'
        )

    def handle(self, *args, **options):
        horas = options.get('horas')
        solo_cola = options.get('cola')

        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('ESTADÍSTICAS DEL SISTEMA M/M/1 - ADONAI CHATBOT'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        if solo_cola:
            # Mostrar solo la cola actual
            estadisticas = obtener_estadisticas_cola()
            self._mostrar_estadisticas_cola(estadisticas)
        else:
            # Mostrar todo
            resumen = obtener_resumen_metricas()
            
            # Métricas teóricas
            self.stdout.write(self.style.WARNING('\n📊 MÉTRICAS M/M/1 (últimas {} horas)'.format(horas)))
            self.stdout.write('-' * 60)
            metricas = resumen['metricas_mm1']
            
            if metricas['estado'] == 'sin_datos':
                self.stdout.write(self.style.WARNING('No hay datos suficientes para calcular métricas'))
            else:
                self.stdout.write(f"  λ (Tasa llegada)          : {metricas['λ (Tasa llegada)']} clientes/hora")
                self.stdout.write(f"  μ (Tasa servicio)         : {metricas['μ (Tasa servicio)']} clientes/hora")
                self.stdout.write(f"  ρ (Utilización servidor)  : {metricas['ρ (Utilización)']} ({metricas['ρ (Utilización)'] * 100:.1f}%)")
                self.stdout.write(f"  Lq (Clientes en cola)     : {metricas['Lq (Clientes en cola)']}")
                self.stdout.write(f"  Wq (Espera en cola)       : {metricas['Wq (Espera promedio)']:.2f} horas")
                self.stdout.write(f"  Ws (Tiempo total sistema) : {metricas['Ws (Tiempo total)']:.2f} horas")
                self.stdout.write(f"  Total chats               : {metricas['total_chats']}")
                self.stdout.write(f"  Chats completados        : {metricas['chats_completados']}")
                self.stdout.write(f"  Tiempo promedio servicio : {metricas['tiempo_promedio_servicio']:.2f} segundos")
            
            # Estadísticas de la cola actual
            estadisticas = resumen['estadisticas_cola_actual']
            self._mostrar_estadisticas_cola(estadisticas)

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))

    def _mostrar_estadisticas_cola(self, estadisticas):
        """Mostrar estadísticas de la cola actual"""
        self.stdout.write(self.style.WARNING('\n📋 ESTADO ACTUAL DE LA COLA'))
        self.stdout.write('-' * 60)
        self.stdout.write(f"  En espera                 : {estadisticas['en_cola']}")
        self.stdout.write(f"  En atención               : {estadisticas['en_atencion']}")
        self.stdout.write(f"  Finalizados               : {estadisticas['finalizados']}")
        self.stdout.write(f"  Tiempo espera promedio    : {estadisticas['tiempo_espera_promedio_minutos']:.2f} minutos")
        
        if estadisticas['servidor_disponible']:
            self.stdout.write(self.style.SUCCESS("  🟢 Servidor DISPONIBLE"))
        else:
            self.stdout.write(self.style.WARNING("  🔴 Servidor OCUPADO"))
