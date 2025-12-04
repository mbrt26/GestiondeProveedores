import uuid
from django.db import models
from apps.core.models import Usuario
from apps.empresas.models import EmpresaAncla


class PlantillaNotificacion(models.Model):
    """Plantillas para notificaciones del sistema."""

    class TipoNotificacion(models.TextChoices):
        EMAIL = 'EMAIL', 'Correo Electrónico'
        WHATSAPP = 'WHATSAPP', 'WhatsApp'
        SISTEMA = 'SISTEMA', 'Notificación del Sistema'

    class Evento(models.TextChoices):
        BIENVENIDA = 'BIENVENIDA', 'Bienvenida al Sistema'
        NUEVO_PROYECTO = 'NUEVO_PROYECTO', 'Asignación a Proyecto'
        CAMBIO_ETAPA = 'CAMBIO_ETAPA', 'Cambio de Etapa'
        TAREA_ASIGNADA = 'TAREA_ASIGNADA', 'Tarea Asignada'
        TAREA_VENCIDA = 'TAREA_VENCIDA', 'Tarea Vencida'
        SESION_PROGRAMADA = 'SESION_PROGRAMADA', 'Sesión Programada'
        TALLER_INSCRIPCION = 'TALLER_INSCRIPCION', 'Inscripción a Taller'
        TALLER_RECORDATORIO = 'TALLER_RECORDATORIO', 'Recordatorio de Taller'
        CERTIFICADO_DISPONIBLE = 'CERTIFICADO_DISPONIBLE', 'Certificado Disponible'
        REPORTE_GENERADO = 'REPORTE_GENERADO', 'Reporte Generado'
        ALERTA_KPI = 'ALERTA_KPI', 'Alerta de KPI'
        PROYECTO_FINALIZADO = 'PROYECTO_FINALIZADO', 'Proyecto Finalizado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField('Nombre', max_length=200)
    evento = models.CharField('Evento', max_length=30, choices=Evento.choices)
    tipo = models.CharField('Tipo', max_length=15, choices=TipoNotificacion.choices)
    asunto = models.CharField('Asunto', max_length=255, blank=True)
    contenido = models.TextField('Contenido')
    contenido_html = models.TextField('Contenido HTML', blank=True)
    variables_disponibles = models.JSONField('Variables Disponibles', default=list)
    is_active = models.BooleanField('Activa', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Plantilla de Notificación'
        verbose_name_plural = 'Plantillas de Notificaciones'
        unique_together = ['evento', 'tipo']

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class Notificacion(models.Model):
    """Notificaciones enviadas a usuarios."""

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        ENVIADA = 'ENVIADA', 'Enviada'
        LEIDA = 'LEIDA', 'Leída'
        FALLIDA = 'FALLIDA', 'Fallida'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='notificaciones'
    )
    plantilla = models.ForeignKey(
        PlantillaNotificacion, on_delete=models.SET_NULL, null=True, blank=True
    )
    tipo = models.CharField(
        'Tipo', max_length=15,
        choices=PlantillaNotificacion.TipoNotificacion.choices
    )
    titulo = models.CharField('Título', max_length=255)
    mensaje = models.TextField('Mensaje')
    datos = models.JSONField('Datos Adicionales', default=dict)
    enlace = models.URLField('Enlace', blank=True)
    estado = models.CharField(
        'Estado', max_length=15,
        choices=Estado.choices, default=Estado.PENDIENTE
    )
    fecha_programada = models.DateTimeField('Fecha Programada', null=True, blank=True)
    fecha_envio = models.DateTimeField('Fecha de Envío', null=True, blank=True)
    fecha_lectura = models.DateTimeField('Fecha de Lectura', null=True, blank=True)
    intentos = models.PositiveSmallIntegerField('Intentos', default=0)
    error_mensaje = models.TextField('Mensaje de Error', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titulo} - {self.usuario.email}"

    def marcar_como_leida(self):
        """Marca la notificación como leída."""
        from django.utils import timezone
        if self.estado != self.Estado.LEIDA:
            self.estado = self.Estado.LEIDA
            self.fecha_lectura = timezone.now()
            self.save(update_fields=['estado', 'fecha_lectura'])


class ConfiguracionNotificacion(models.Model):
    """Configuración de notificaciones por usuario."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name='config_notificaciones'
    )
    email_activo = models.BooleanField('Recibir por Email', default=True)
    whatsapp_activo = models.BooleanField('Recibir por WhatsApp', default=False)
    sistema_activo = models.BooleanField('Notificaciones del Sistema', default=True)

    # Preferencias por tipo de evento
    notificar_tareas = models.BooleanField('Notificar Tareas', default=True)
    notificar_sesiones = models.BooleanField('Notificar Sesiones', default=True)
    notificar_talleres = models.BooleanField('Notificar Talleres', default=True)
    notificar_reportes = models.BooleanField('Notificar Reportes', default=True)
    notificar_alertas = models.BooleanField('Notificar Alertas', default=True)

    # Horario de no molestar
    horario_no_molestar_inicio = models.TimeField(
        'No Molestar Desde', null=True, blank=True
    )
    horario_no_molestar_fin = models.TimeField(
        'No Molestar Hasta', null=True, blank=True
    )

    class Meta:
        verbose_name = 'Configuración de Notificación'
        verbose_name_plural = 'Configuraciones de Notificaciones'

    def __str__(self):
        return f"Configuración de {self.usuario.email}"


class ColaNotificacion(models.Model):
    """Cola de notificaciones para procesamiento asíncrono."""

    class Prioridad(models.IntegerChoices):
        BAJA = 1, 'Baja'
        NORMAL = 2, 'Normal'
        ALTA = 3, 'Alta'
        URGENTE = 4, 'Urgente'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notificacion = models.OneToOneField(
        Notificacion, on_delete=models.CASCADE, related_name='cola'
    )
    prioridad = models.PositiveSmallIntegerField(
        'Prioridad', choices=Prioridad.choices, default=Prioridad.NORMAL
    )
    procesado = models.BooleanField('Procesado', default=False)
    fecha_procesamiento = models.DateTimeField('Fecha de Procesamiento', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cola de Notificación'
        verbose_name_plural = 'Cola de Notificaciones'
        ordering = ['-prioridad', 'created_at']

    def __str__(self):
        return f"Cola: {self.notificacion.titulo}"


class ConfiguracionEmail(models.Model):
    """Configuración de servidor de email (Google Workspace)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa_ancla = models.OneToOneField(
        EmpresaAncla, on_delete=models.CASCADE,
        related_name='config_email', null=True, blank=True
    )
    nombre = models.CharField('Nombre', max_length=100, default='Principal')
    email_remitente = models.EmailField('Email Remitente')
    nombre_remitente = models.CharField('Nombre Remitente', max_length=100)
    servidor_smtp = models.CharField('Servidor SMTP', max_length=255, default='smtp.gmail.com')
    puerto_smtp = models.PositiveIntegerField('Puerto SMTP', default=587)
    usar_tls = models.BooleanField('Usar TLS', default=True)
    credenciales = models.JSONField('Credenciales', default=dict)
    is_active = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Configuración de Email'
        verbose_name_plural = 'Configuraciones de Email'

    def __str__(self):
        return f"{self.nombre} - {self.email_remitente}"


class ConfiguracionWhatsApp(models.Model):
    """Configuración de WhatsApp Business API."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa_ancla = models.OneToOneField(
        EmpresaAncla, on_delete=models.CASCADE,
        related_name='config_whatsapp', null=True, blank=True
    )
    nombre = models.CharField('Nombre', max_length=100, default='Principal')
    numero_telefono = models.CharField('Número de Teléfono', max_length=20)
    api_url = models.URLField('URL de API')
    api_key = models.CharField('API Key', max_length=255)
    webhook_secret = models.CharField('Webhook Secret', max_length=255, blank=True)
    is_active = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Configuración de WhatsApp'
        verbose_name_plural = 'Configuraciones de WhatsApp'

    def __str__(self):
        return f"{self.nombre} - {self.numero_telefono}"


class HistorialEnvio(models.Model):
    """Historial de envíos de notificaciones."""

    class Canal(models.TextChoices):
        EMAIL = 'EMAIL', 'Email'
        WHATSAPP = 'WHATSAPP', 'WhatsApp'
        SISTEMA = 'SISTEMA', 'Sistema'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notificacion = models.ForeignKey(
        Notificacion, on_delete=models.CASCADE, related_name='historial_envios'
    )
    canal = models.CharField('Canal', max_length=15, choices=Canal.choices)
    destinatario = models.CharField('Destinatario', max_length=255)
    exitoso = models.BooleanField('Exitoso', default=False)
    respuesta_servidor = models.TextField('Respuesta del Servidor', blank=True)
    mensaje_id_externo = models.CharField('ID Mensaje Externo', max_length=255, blank=True)
    fecha_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Historial de Envío'
        verbose_name_plural = 'Historial de Envíos'
        ordering = ['-fecha_envio']

    def __str__(self):
        return f"{self.canal} -> {self.destinatario}"
