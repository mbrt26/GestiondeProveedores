"""
Servicios para envío de notificaciones.
"""
import logging
from string import Template
from typing import Optional, Dict, Any, List

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from .models import (
    Notificacion, PlantillaNotificacion, ConfiguracionNotificacion,
    ColaNotificacion, HistorialEnvio, ConfiguracionEmail, ConfiguracionWhatsApp
)
from apps.core.models import Usuario

logger = logging.getLogger(__name__)


class NotificacionService:
    """Servicio principal para gestión de notificaciones."""

    @classmethod
    def crear_notificacion(
        cls,
        usuario: Usuario,
        evento: str,
        datos: Dict[str, Any],
        tipos: Optional[List[str]] = None,
        prioridad: int = 2,
        enlace: str = ''
    ) -> List[Notificacion]:
        """
        Crea notificaciones para un usuario según el evento.

        Args:
            usuario: Usuario destinatario
            evento: Tipo de evento (ver PlantillaNotificacion.Evento)
            datos: Diccionario con variables para la plantilla
            tipos: Lista de tipos de notificación (EMAIL, WHATSAPP, SISTEMA)
            prioridad: Prioridad de la notificación (1-4)
            enlace: URL opcional para la notificación

        Returns:
            Lista de notificaciones creadas
        """
        # Obtener configuración del usuario
        config, _ = ConfiguracionNotificacion.objects.get_or_create(usuario=usuario)

        # Determinar tipos de notificación
        if tipos is None:
            tipos = []
            if config.email_activo:
                tipos.append('EMAIL')
            if config.whatsapp_activo:
                tipos.append('WHATSAPP')
            if config.sistema_activo:
                tipos.append('SISTEMA')

        notificaciones = []

        for tipo in tipos:
            # Buscar plantilla
            plantilla = PlantillaNotificacion.objects.filter(
                evento=evento, tipo=tipo, is_active=True
            ).first()

            if not plantilla:
                logger.warning(f"No hay plantilla activa para evento={evento}, tipo={tipo}")
                continue

            # Renderizar contenido
            titulo = cls._renderizar_texto(plantilla.asunto, datos)
            mensaje = cls._renderizar_texto(plantilla.contenido, datos)

            # Crear notificación
            notificacion = Notificacion.objects.create(
                usuario=usuario,
                plantilla=plantilla,
                tipo=tipo,
                titulo=titulo,
                mensaje=mensaje,
                datos=datos,
                enlace=enlace,
                estado=Notificacion.Estado.PENDIENTE
            )

            # Agregar a cola
            ColaNotificacion.objects.create(
                notificacion=notificacion,
                prioridad=prioridad
            )

            notificaciones.append(notificacion)

        return notificaciones

    @classmethod
    def _renderizar_texto(cls, texto: str, datos: Dict[str, Any]) -> str:
        """Renderiza texto con variables."""
        try:
            template = Template(texto)
            return template.safe_substitute(datos)
        except Exception as e:
            logger.error(f"Error renderizando texto: {e}")
            return texto

    @classmethod
    def procesar_cola(cls, limite: int = 100) -> Dict[str, int]:
        """
        Procesa la cola de notificaciones pendientes.

        Args:
            limite: Número máximo de notificaciones a procesar

        Returns:
            Diccionario con estadísticas de procesamiento
        """
        stats = {'procesadas': 0, 'exitosas': 0, 'fallidas': 0}

        cola_items = ColaNotificacion.objects.filter(
            procesado=False
        ).select_related('notificacion').order_by('-prioridad', 'created_at')[:limite]

        for item in cola_items:
            notificacion = item.notificacion
            exito = False

            try:
                if notificacion.tipo == 'EMAIL':
                    exito = cls._enviar_email(notificacion)
                elif notificacion.tipo == 'WHATSAPP':
                    exito = cls._enviar_whatsapp(notificacion)
                elif notificacion.tipo == 'SISTEMA':
                    # Las notificaciones del sistema solo se marcan como enviadas
                    exito = True

                if exito:
                    notificacion.estado = Notificacion.Estado.ENVIADA
                    notificacion.fecha_envio = timezone.now()
                    stats['exitosas'] += 1
                else:
                    notificacion.intentos += 1
                    if notificacion.intentos >= 3:
                        notificacion.estado = Notificacion.Estado.FALLIDA
                    stats['fallidas'] += 1

                notificacion.save()

            except Exception as e:
                logger.error(f"Error procesando notificación {notificacion.id}: {e}")
                notificacion.intentos += 1
                notificacion.error_mensaje = str(e)
                notificacion.save()
                stats['fallidas'] += 1

            item.procesado = True
            item.fecha_procesamiento = timezone.now()
            item.save()
            stats['procesadas'] += 1

        return stats

    @classmethod
    def _enviar_email(cls, notificacion: Notificacion) -> bool:
        """Envía notificación por email."""
        try:
            # Obtener configuración de email
            config_email = ConfiguracionEmail.objects.filter(is_active=True).first()

            if not config_email:
                logger.error("No hay configuración de email activa")
                return False

            # Preparar email
            email = EmailMultiAlternatives(
                subject=notificacion.titulo,
                body=notificacion.mensaje,
                from_email=f"{config_email.nombre_remitente} <{config_email.email_remitente}>",
                to=[notificacion.usuario.email]
            )

            # Agregar versión HTML si la plantilla tiene contenido HTML
            if notificacion.plantilla and notificacion.plantilla.contenido_html:
                html_content = cls._renderizar_texto(
                    notificacion.plantilla.contenido_html,
                    notificacion.datos
                )
                email.attach_alternative(html_content, "text/html")

            email.send()

            # Registrar historial
            HistorialEnvio.objects.create(
                notificacion=notificacion,
                canal='EMAIL',
                destinatario=notificacion.usuario.email,
                exitoso=True
            )

            return True

        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            HistorialEnvio.objects.create(
                notificacion=notificacion,
                canal='EMAIL',
                destinatario=notificacion.usuario.email,
                exitoso=False,
                respuesta_servidor=str(e)
            )
            return False

    @classmethod
    def _enviar_whatsapp(cls, notificacion: Notificacion) -> bool:
        """Envía notificación por WhatsApp."""
        try:
            import requests

            # Obtener configuración de WhatsApp
            config_wa = ConfiguracionWhatsApp.objects.filter(is_active=True).first()

            if not config_wa:
                logger.error("No hay configuración de WhatsApp activa")
                return False

            # Obtener número de teléfono del usuario
            telefono = notificacion.usuario.telefono
            if not telefono:
                logger.error(f"Usuario {notificacion.usuario.id} no tiene teléfono")
                return False

            # Preparar request a API de WhatsApp
            headers = {
                'Authorization': f'Bearer {config_wa.api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'messaging_product': 'whatsapp',
                'to': telefono,
                'type': 'text',
                'text': {
                    'body': notificacion.mensaje
                }
            }

            response = requests.post(
                config_wa.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            exito = response.status_code == 200

            # Registrar historial
            HistorialEnvio.objects.create(
                notificacion=notificacion,
                canal='WHATSAPP',
                destinatario=telefono,
                exitoso=exito,
                respuesta_servidor=response.text,
                mensaje_id_externo=response.json().get('messages', [{}])[0].get('id', '') if exito else ''
            )

            return exito

        except Exception as e:
            logger.error(f"Error enviando WhatsApp: {e}")
            HistorialEnvio.objects.create(
                notificacion=notificacion,
                canal='WHATSAPP',
                destinatario=notificacion.usuario.telefono or '',
                exitoso=False,
                respuesta_servidor=str(e)
            )
            return False


def notificar_cambio_etapa(proveedor_proyecto, etapa_anterior: int, etapa_nueva: int):
    """Helper para notificar cambio de etapa."""
    from apps.proyectos.models import ProveedorProyecto

    etapas = dict(ProveedorProyecto._meta.get_field('etapa_actual').choices)

    datos = {
        'proveedor': proveedor_proyecto.proveedor.razon_social,
        'proyecto': proveedor_proyecto.proyecto.nombre,
        'etapa_anterior': etapas.get(etapa_anterior, str(etapa_anterior)),
        'etapa_nueva': etapas.get(etapa_nueva, str(etapa_nueva)),
    }

    # Notificar al usuario del proveedor
    if proveedor_proyecto.proveedor.usuario_principal:
        NotificacionService.crear_notificacion(
            usuario=proveedor_proyecto.proveedor.usuario_principal,
            evento='CAMBIO_ETAPA',
            datos=datos,
            prioridad=3
        )


def notificar_tarea_asignada(tarea):
    """Helper para notificar tarea asignada."""
    if not tarea.responsable:
        return

    datos = {
        'tarea': tarea.titulo,
        'proveedor': tarea.implementacion.proveedor_proyecto.proveedor.razon_social,
        'fecha_limite': tarea.fecha_limite.strftime('%d/%m/%Y') if tarea.fecha_limite else 'Sin fecha',
    }

    NotificacionService.crear_notificacion(
        usuario=tarea.responsable,
        evento='TAREA_ASIGNADA',
        datos=datos,
        prioridad=2
    )


def notificar_sesion_programada(sesion):
    """Helper para notificar sesión programada."""
    proveedor_proyecto = sesion.implementacion.proveedor_proyecto

    datos = {
        'tipo_sesion': sesion.get_tipo_display(),
        'fecha': sesion.fecha_programada.strftime('%d/%m/%Y %H:%M'),
        'proveedor': proveedor_proyecto.proveedor.razon_social,
    }

    # Notificar al proveedor
    if proveedor_proyecto.proveedor.usuario_principal:
        NotificacionService.crear_notificacion(
            usuario=proveedor_proyecto.proveedor.usuario_principal,
            evento='SESION_PROGRAMADA',
            datos=datos,
            prioridad=3
        )
