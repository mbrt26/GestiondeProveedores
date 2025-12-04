import uuid
from django.db import models
from apps.core.models import AuditoriaModel, Usuario
from apps.proyectos.models import Proyecto
from apps.proveedores.models import Proveedor


class Taller(AuditoriaModel):
    """Modelo para talleres especializados."""

    class TipoTaller(models.TextChoices):
        GESTION_RIESGOS = 'GESTION_RIESGOS', 'Gestión de Riesgos y Manejo de Crisis'
        TRANSFORMACION_DIGITAL = 'TRANSFORMACION_DIGITAL', 'Transformación Digital'
        MEJORA_CONTINUA = 'MEJORA_CONTINUA', 'Mejora Continua'
        SOSTENIBILIDAD = 'SOSTENIBILIDAD', 'Sostenibilidad Empresarial'
        OTRO = 'OTRO', 'Otro'

    class Modalidad(models.TextChoices):
        PRESENCIAL = 'PRESENCIAL', 'Presencial'
        VIRTUAL = 'VIRTUAL', 'Virtual'
        HIBRIDO = 'HIBRIDO', 'Híbrido'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField('Nombre del taller', max_length=200)
    tipo = models.CharField('Tipo', max_length=25, choices=TipoTaller.choices, default=TipoTaller.OTRO)
    descripcion = models.TextField('Descripción')
    contenido_programatico = models.TextField('Contenido programático', blank=True)
    objetivos = models.TextField('Objetivos', blank=True)
    duracion_horas = models.DecimalField('Duración (horas)', max_digits=4, decimal_places=1, default=4)
    modalidad = models.CharField('Modalidad', max_length=15, choices=Modalidad.choices, default=Modalidad.PRESENCIAL)
    capacidad_maxima = models.PositiveIntegerField('Capacidad máxima', default=40)
    facilitador = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='talleres_facilitados', verbose_name='Facilitador'
    )
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='talleres', verbose_name='Proyecto asociado'
    )
    material_didactico = models.FileField('Material didáctico', upload_to='talleres/materiales/', blank=True, null=True)
    is_active = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Taller'
        verbose_name_plural = 'Talleres'
        ordering = ['-created_at']

    def __str__(self):
        return self.nombre


class SesionTaller(models.Model):
    """Sesiones programadas de un taller."""

    class Estado(models.TextChoices):
        PROGRAMADA = 'PROGRAMADA', 'Programada'
        EN_CURSO = 'EN_CURSO', 'En curso'
        FINALIZADA = 'FINALIZADA', 'Finalizada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    taller = models.ForeignKey(Taller, on_delete=models.CASCADE, related_name='sesiones', verbose_name='Taller')
    fecha = models.DateField('Fecha')
    hora_inicio = models.TimeField('Hora de inicio')
    hora_fin = models.TimeField('Hora de fin')
    lugar = models.CharField('Lugar/Link', max_length=300)
    estado = models.CharField('Estado', max_length=15, choices=Estado.choices, default=Estado.PROGRAMADA)
    notas = models.TextField('Notas', blank=True)
    grabacion_url = models.URLField('URL de grabación', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Sesión de Taller'
        verbose_name_plural = 'Sesiones de Talleres'
        ordering = ['-fecha', '-hora_inicio']

    def __str__(self):
        return f"{self.taller.nombre} - {self.fecha}"

    @property
    def inscritos_count(self):
        return self.inscripciones.exclude(estado='CANCELADO').count()


class InscripcionTaller(models.Model):
    """Inscripciones a sesiones de talleres."""

    class Estado(models.TextChoices):
        INSCRITO = 'INSCRITO', 'Inscrito'
        CONFIRMADO = 'CONFIRMADO', 'Confirmado'
        ASISTIO = 'ASISTIO', 'Asistió'
        NO_ASISTIO = 'NO_ASISTIO', 'No asistió'
        CANCELADO = 'CANCELADO', 'Cancelado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sesion = models.ForeignKey(SesionTaller, on_delete=models.CASCADE, related_name='inscripciones')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='inscripciones_talleres')
    participante_nombre = models.CharField('Nombre del participante', max_length=200)
    participante_email = models.EmailField('Email')
    participante_cargo = models.CharField('Cargo', max_length=100, blank=True)
    estado = models.CharField('Estado', max_length=15, choices=Estado.choices, default=Estado.INSCRITO)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    confirmacion_enviada = models.BooleanField('Confirmación enviada', default=False)

    class Meta:
        verbose_name = 'Inscripción'
        verbose_name_plural = 'Inscripciones'
        unique_together = ['sesion', 'participante_email']

    def __str__(self):
        return f"{self.participante_nombre} - {self.sesion}"


class AsistenciaTaller(models.Model):
    """Control de asistencia."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscripcion = models.OneToOneField(InscripcionTaller, on_delete=models.CASCADE, related_name='asistencia')
    hora_entrada = models.TimeField('Hora de entrada', null=True, blank=True)
    hora_salida = models.TimeField('Hora de salida', null=True, blank=True)
    asistio = models.BooleanField('Asistió', default=False)
    observaciones = models.TextField('Observaciones', blank=True)

    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'

    def __str__(self):
        return f"Asistencia: {self.inscripcion.participante_nombre}"


class CertificadoTaller(models.Model):
    """Certificados de participación."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscripcion = models.OneToOneField(InscripcionTaller, on_delete=models.CASCADE, related_name='certificado')
    codigo_certificado = models.CharField('Código', max_length=50, unique=True)
    fecha_emision = models.DateTimeField('Fecha de emisión', auto_now_add=True)
    archivo_pdf = models.FileField('PDF', upload_to='talleres/certificados/', blank=True, null=True)
    enviado = models.BooleanField('Enviado', default=False)
    fecha_envio = models.DateTimeField('Fecha de envío', null=True, blank=True)

    class Meta:
        verbose_name = 'Certificado'
        verbose_name_plural = 'Certificados'

    def __str__(self):
        return self.codigo_certificado


class EvaluacionTaller(models.Model):
    """Evaluaciones post-taller."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscripcion = models.OneToOneField(InscripcionTaller, on_delete=models.CASCADE, related_name='evaluacion')
    calificacion_general = models.PositiveSmallIntegerField('Calificación general', choices=[(i, str(i)) for i in range(1, 6)])
    calificacion_facilitador = models.PositiveSmallIntegerField('Facilitador', choices=[(i, str(i)) for i in range(1, 6)])
    calificacion_contenido = models.PositiveSmallIntegerField('Contenido', choices=[(i, str(i)) for i in range(1, 6)])
    calificacion_logistica = models.PositiveSmallIntegerField('Logística', choices=[(i, str(i)) for i in range(1, 6)])
    comentarios = models.TextField('Comentarios', blank=True)
    sugerencias = models.TextField('Sugerencias', blank=True)
    fecha_evaluacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Evaluación de Taller'
        verbose_name_plural = 'Evaluaciones de Talleres'

    def __str__(self):
        return f"Evaluación: {self.inscripcion.participante_nombre}"
