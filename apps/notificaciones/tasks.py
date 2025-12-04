"""
Tareas de Celery para notificaciones.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def procesar_cola_notificaciones():
    """Procesa la cola de notificaciones pendientes."""
    from .services import NotificacionService

    stats = NotificacionService.procesar_cola(limite=100)
    logger.info(f"Cola procesada: {stats}")
    return stats


@shared_task
def enviar_recordatorios_tareas():
    """Envía recordatorios de tareas próximas a vencer."""
    from apps.etapas.models import TareaImplementacion
    from apps.notificaciones.services import NotificacionService

    # Tareas que vencen mañana
    manana = timezone.now().date() + timedelta(days=1)

    tareas = TareaImplementacion.objects.filter(
        fecha_limite=manana,
        estado__in=['PENDIENTE', 'EN_PROGRESO']
    ).select_related('responsable', 'implementacion__proveedor_proyecto__proveedor')

    for tarea in tareas:
        if tarea.responsable:
            NotificacionService.crear_notificacion(
                usuario=tarea.responsable,
                evento='TAREA_VENCIDA',
                datos={
                    'tarea': tarea.titulo,
                    'fecha_limite': tarea.fecha_limite.strftime('%d/%m/%Y'),
                    'proveedor': tarea.implementacion.proveedor_proyecto.proveedor.razon_social,
                },
                prioridad=3
            )

    return f"Recordatorios enviados: {tareas.count()}"


@shared_task
def enviar_recordatorios_talleres():
    """Envía recordatorios de talleres próximos."""
    from apps.talleres.models import SesionTaller, InscripcionTaller
    from apps.notificaciones.services import NotificacionService

    # Sesiones que inician mañana
    manana = timezone.now().date() + timedelta(days=1)

    sesiones = SesionTaller.objects.filter(
        fecha=manana,
        estado='PROGRAMADA'
    ).select_related('taller')

    for sesion in sesiones:
        inscripciones = InscripcionTaller.objects.filter(
            taller=sesion.taller,
            estado='CONFIRMADA'
        ).select_related('usuario')

        for inscripcion in inscripciones:
            NotificacionService.crear_notificacion(
                usuario=inscripcion.usuario,
                evento='TALLER_RECORDATORIO',
                datos={
                    'taller': sesion.taller.nombre,
                    'fecha': sesion.fecha.strftime('%d/%m/%Y'),
                    'hora': sesion.hora_inicio.strftime('%H:%M'),
                    'modalidad': sesion.taller.get_modalidad_display(),
                    'lugar': sesion.lugar or sesion.enlace_virtual or 'Por confirmar',
                },
                prioridad=3
            )

    return f"Recordatorios de talleres enviados para {sesiones.count()} sesiones"


@shared_task
def generar_reportes_automaticos():
    """Genera reportes automáticos según configuración."""
    from apps.reportes.models import ConfiguracionReporteAutomatico
    from apps.notificaciones.services import NotificacionService

    hoy = timezone.now()
    dia_semana = hoy.weekday()  # 0 = Lunes

    configs = ConfiguracionReporteAutomatico.objects.filter(
        is_active=True
    ).select_related('empresa_ancla')

    for config in configs:
        debe_generar = False

        if config.frecuencia == 'DIARIO':
            debe_generar = True
        elif config.frecuencia == 'SEMANAL' and dia_semana == 0:  # Lunes
            debe_generar = True
        elif config.frecuencia == 'QUINCENAL' and hoy.day in [1, 15]:
            debe_generar = True
        elif config.frecuencia == 'MENSUAL' and hoy.day == 1:
            debe_generar = True

        if debe_generar:
            # TODO: Implementar generación de reporte
            logger.info(f"Generando reporte {config.tipo_reporte} para {config.empresa_ancla}")

            # Notificar a destinatarios
            for email in config.destinatarios:
                logger.info(f"Enviando reporte a {email}")

    return "Reportes automáticos procesados"


@shared_task
def limpiar_notificaciones_antiguas(dias: int = 90):
    """Elimina notificaciones antiguas."""
    from .models import Notificacion

    fecha_limite = timezone.now() - timedelta(days=dias)

    deleted, _ = Notificacion.objects.filter(
        created_at__lt=fecha_limite,
        estado='LEIDA'
    ).delete()

    logger.info(f"Notificaciones eliminadas: {deleted}")
    return f"Eliminadas {deleted} notificaciones antiguas"
