import uuid
from django.db import models
from django.utils import timezone
from apps.core.models import Usuario
from apps.proyectos.models import ProveedorProyecto


# ============================================================================
# ETAPA 1: DIAGNÓSTICO DE COMPETITIVIDAD
# ============================================================================

class Etapa1Diagnostico(models.Model):
    """Etapa 1: Diagnóstico de Competitividad."""

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_PROCESO = 'EN_PROCESO', 'En proceso'
        COMPLETADO = 'COMPLETADO', 'Completado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proveedor_proyecto = models.OneToOneField(
        ProveedorProyecto,
        on_delete=models.CASCADE,
        related_name='etapa1',
        verbose_name='Proveedor en Proyecto'
    )
    estado = models.CharField(
        'Estado',
        max_length=15,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )
    fecha_inicio = models.DateTimeField('Fecha de inicio', null=True, blank=True)
    fecha_fin = models.DateTimeField('Fecha de finalización', null=True, blank=True)
    completado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='etapas1_completadas',
        verbose_name='Completado por'
    )
    observaciones = models.TextField('Observaciones', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Etapa 1 - Diagnóstico'
        verbose_name_plural = 'Etapas 1 - Diagnósticos'

    def __str__(self):
        return f"E1: {self.proveedor_proyecto}"

    def iniciar(self):
        if self.estado == self.Estado.PENDIENTE:
            self.estado = self.Estado.EN_PROCESO
            self.fecha_inicio = timezone.now()
            self.save()

    def completar(self, usuario):
        if self.estado == self.Estado.EN_PROCESO:
            self.estado = self.Estado.COMPLETADO
            self.fecha_fin = timezone.now()
            self.completado_por = usuario
            self.save()
            # Crear Etapa 2
            Etapa2Plan.objects.get_or_create(proveedor_proyecto=self.proveedor_proyecto)


class VozCliente(models.Model):
    """Registro de la voz del cliente (empresa ancla)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etapa1 = models.ForeignKey(
        Etapa1Diagnostico,
        on_delete=models.CASCADE,
        related_name='voces_cliente',
        verbose_name='Etapa 1'
    )
    empresa_ancla_contacto = models.CharField('Contacto de empresa ancla', max_length=200)
    cargo_contacto = models.CharField('Cargo del contacto', max_length=100, blank=True)
    fecha_entrevista = models.DateField('Fecha de entrevista')
    necesidades_identificadas = models.TextField('Necesidades identificadas')
    expectativas = models.TextField('Expectativas')
    requerimientos_especificos = models.TextField('Requerimientos específicos', blank=True)
    fortalezas_proveedor = models.TextField('Fortalezas del proveedor', blank=True)
    areas_mejora = models.TextField('Áreas de mejora identificadas', blank=True)
    archivo_evidencia = models.FileField(
        'Archivo de evidencia',
        upload_to='etapas/voz_cliente/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Voz del Cliente'
        verbose_name_plural = 'Voces del Cliente'
        ordering = ['-fecha_entrevista']

    def __str__(self):
        return f"Voz Cliente: {self.etapa1.proveedor_proyecto.proveedor} - {self.fecha_entrevista}"


class DiagnosticoCompetitividad(models.Model):
    """Diagnóstico de competitividad por áreas."""

    class AreaEvaluada(models.TextChoices):
        ESTRATEGIA = 'ESTRATEGIA', 'Estrategia y Dirección'
        COMERCIAL = 'COMERCIAL', 'Gestión Comercial'
        OPERACIONES = 'OPERACIONES', 'Operaciones y Producción'
        FINANCIERO = 'FINANCIERO', 'Gestión Financiera'
        TALENTO = 'TALENTO', 'Talento Humano'
        CALIDAD = 'CALIDAD', 'Gestión de Calidad'
        INNOVACION = 'INNOVACION', 'Innovación y Tecnología'
        SOSTENIBILIDAD = 'SOSTENIBILIDAD', 'Sostenibilidad'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etapa1 = models.ForeignKey(
        Etapa1Diagnostico,
        on_delete=models.CASCADE,
        related_name='diagnosticos',
        verbose_name='Etapa 1'
    )
    area_evaluada = models.CharField(
        'Área evaluada',
        max_length=20,
        choices=AreaEvaluada.choices
    )
    nivel_madurez = models.PositiveSmallIntegerField(
        'Nivel de madurez',
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text='1=Inicial, 2=Básico, 3=Definido, 4=Gestionado, 5=Optimizado'
    )
    puntaje = models.DecimalField('Puntaje', max_digits=5, decimal_places=2, default=0)
    fortalezas = models.TextField('Fortalezas', blank=True)
    debilidades = models.TextField('Debilidades', blank=True)
    oportunidades = models.TextField('Oportunidades', blank=True)
    amenazas = models.TextField('Amenazas', blank=True)
    observaciones = models.TextField('Observaciones', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Diagnóstico de Competitividad'
        verbose_name_plural = 'Diagnósticos de Competitividad'
        unique_together = ['etapa1', 'area_evaluada']

    def __str__(self):
        return f"{self.etapa1.proveedor_proyecto.proveedor} - {self.get_area_evaluada_display()}"


class ObjetivoFortalecimiento(models.Model):
    """Objetivos SMART del fortalecimiento."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etapa1 = models.ForeignKey(
        Etapa1Diagnostico,
        on_delete=models.CASCADE,
        related_name='objetivos',
        verbose_name='Etapa 1'
    )
    objetivo = models.TextField('Objetivo')
    especifico = models.TextField('Específico (qué se quiere lograr)', blank=True)
    medible = models.CharField('Medible (indicador)', max_length=200)
    alcanzable = models.TextField('Alcanzable (cómo se logrará)', blank=True)
    relevante = models.TextField('Relevante (por qué es importante)', blank=True)
    temporal = models.CharField('Temporal (plazo)', max_length=100, blank=True)
    valor_inicial = models.DecimalField('Valor inicial', max_digits=10, decimal_places=2, default=0)
    valor_meta = models.DecimalField('Valor meta', max_digits=10, decimal_places=2, default=0)
    unidad_medida = models.CharField('Unidad de medida', max_length=50, blank=True)
    prioridad = models.PositiveSmallIntegerField('Prioridad', default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Objetivo de Fortalecimiento'
        verbose_name_plural = 'Objetivos de Fortalecimiento'
        ordering = ['prioridad']

    def __str__(self):
        return f"Objetivo: {self.objetivo[:50]}..."


class DocumentoEtapa1(models.Model):
    """Documentos de la Etapa 1."""

    class TipoDocumento(models.TextChoices):
        VOZ_CLIENTE = 'VOZ_CLIENTE', 'Voz del Cliente'
        DIAGNOSTICO = 'DIAGNOSTICO', 'Diagnóstico'
        GRABACION = 'GRABACION', 'Grabación'
        EVIDENCIA = 'EVIDENCIA', 'Evidencia'
        OTRO = 'OTRO', 'Otro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etapa1 = models.ForeignKey(
        Etapa1Diagnostico,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name='Etapa 1'
    )
    tipo = models.CharField('Tipo', max_length=15, choices=TipoDocumento.choices)
    nombre = models.CharField('Nombre', max_length=200)
    archivo = models.FileField('Archivo', upload_to='etapas/etapa1/')
    descripcion = models.TextField('Descripción', blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, verbose_name='Subido por'
    )

    class Meta:
        verbose_name = 'Documento Etapa 1'
        verbose_name_plural = 'Documentos Etapa 1'

    def __str__(self):
        return self.nombre


# ============================================================================
# ETAPA 2: PLAN DE IMPLEMENTACIÓN
# ============================================================================

class Etapa2Plan(models.Model):
    """Etapa 2: Plan de Implementación."""

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_PROCESO = 'EN_PROCESO', 'En proceso'
        EN_REVISION = 'EN_REVISION', 'En revisión'
        APROBADO = 'APROBADO', 'Aprobado'
        RECHAZADO = 'RECHAZADO', 'Rechazado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proveedor_proyecto = models.OneToOneField(
        ProveedorProyecto,
        on_delete=models.CASCADE,
        related_name='etapa2',
        verbose_name='Proveedor en Proyecto'
    )
    estado = models.CharField(
        'Estado',
        max_length=15,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )
    fecha_inicio = models.DateTimeField('Fecha de inicio', null=True, blank=True)
    fecha_fin = models.DateTimeField('Fecha de finalización', null=True, blank=True)
    aprobado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='planes_aprobados',
        verbose_name='Aprobado por'
    )
    fecha_aprobacion = models.DateTimeField('Fecha de aprobación', null=True, blank=True)
    observaciones_aprobacion = models.TextField('Observaciones de aprobación', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Etapa 2 - Plan'
        verbose_name_plural = 'Etapas 2 - Planes'

    def __str__(self):
        return f"E2: {self.proveedor_proyecto}"

    def aprobar(self, usuario, observaciones=''):
        self.estado = self.Estado.APROBADO
        self.aprobado_por = usuario
        self.fecha_aprobacion = timezone.now()
        self.fecha_fin = timezone.now()
        self.observaciones_aprobacion = observaciones
        self.save()
        # Crear Etapa 3
        Etapa3Implementacion.objects.get_or_create(proveedor_proyecto=self.proveedor_proyecto)
        # Avanzar etapa del proveedor
        self.proveedor_proyecto.etapa_actual = 3
        self.proveedor_proyecto.save()


class HallazgoProblema(models.Model):
    """Hallazgo, problema y causa raíz identificados."""

    class Prioridad(models.TextChoices):
        ALTA = 'ALTA', 'Alta'
        MEDIA = 'MEDIA', 'Media'
        BAJA = 'BAJA', 'Baja'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etapa2 = models.ForeignKey(
        Etapa2Plan,
        on_delete=models.CASCADE,
        related_name='hallazgos',
        verbose_name='Etapa 2'
    )
    codigo = models.CharField('Código', max_length=20, blank=True)
    hallazgo = models.TextField('Hallazgo')
    problema_identificado = models.TextField('Problema identificado')
    causa_raiz = models.TextField('Causa raíz')
    area_impactada = models.CharField('Área impactada', max_length=100, blank=True)
    prioridad = models.CharField(
        'Prioridad',
        max_length=10,
        choices=Prioridad.choices,
        default=Prioridad.MEDIA
    )
    orden = models.PositiveSmallIntegerField('Orden', default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Hallazgo/Problema'
        verbose_name_plural = 'Hallazgos/Problemas'
        ordering = ['orden', '-prioridad']

    def __str__(self):
        return f"Hallazgo: {self.hallazgo[:50]}..."

    def save(self, *args, **kwargs):
        if not self.codigo:
            count = HallazgoProblema.objects.filter(etapa2=self.etapa2).count() + 1
            self.codigo = f"H-{count:02d}"
        super().save(*args, **kwargs)


class AccionMejora(models.Model):
    """Acciones de mejora propuestas."""

    class TipoAccion(models.TextChoices):
        CORRECTIVA = 'CORRECTIVA', 'Correctiva'
        PREVENTIVA = 'PREVENTIVA', 'Preventiva'
        MEJORA = 'MEJORA', 'Mejora'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hallazgo = models.ForeignKey(
        HallazgoProblema,
        on_delete=models.CASCADE,
        related_name='acciones',
        verbose_name='Hallazgo'
    )
    descripcion = models.TextField('Descripción de la acción')
    tipo_accion = models.CharField(
        'Tipo de acción',
        max_length=15,
        choices=TipoAccion.choices,
        default=TipoAccion.MEJORA
    )
    recursos_necesarios = models.TextField('Recursos necesarios', blank=True)
    responsable_sugerido = models.CharField('Responsable sugerido', max_length=200, blank=True)
    impacto_esperado = models.PositiveSmallIntegerField(
        'Impacto esperado',
        choices=[(i, str(i)) for i in range(1, 6)],
        default=3,
        help_text='1=Muy bajo, 5=Muy alto'
    )
    esfuerzo_requerido = models.PositiveSmallIntegerField(
        'Esfuerzo requerido',
        choices=[(i, str(i)) for i in range(1, 6)],
        default=3,
        help_text='1=Muy bajo, 5=Muy alto'
    )
    puntuacion_priorizacion = models.DecimalField(
        'Puntuación de priorización',
        max_digits=5,
        decimal_places=2,
        default=0
    )
    seleccionada = models.BooleanField('Seleccionada para implementar', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Acción de Mejora'
        verbose_name_plural = 'Acciones de Mejora'
        ordering = ['-puntuacion_priorizacion']

    def __str__(self):
        return f"Acción: {self.descripcion[:50]}..."

    def save(self, *args, **kwargs):
        # Calcular puntuación: mayor impacto y menor esfuerzo = mejor
        self.puntuacion_priorizacion = (self.impacto_esperado * 2) - self.esfuerzo_requerido
        super().save(*args, **kwargs)


class CronogramaImplementacion(models.Model):
    """Cronograma de implementación de acciones."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etapa2 = models.ForeignKey(
        Etapa2Plan,
        on_delete=models.CASCADE,
        related_name='cronograma',
        verbose_name='Etapa 2'
    )
    accion_mejora = models.ForeignKey(
        AccionMejora,
        on_delete=models.CASCADE,
        related_name='cronograma_items',
        verbose_name='Acción de mejora'
    )
    actividad = models.CharField('Actividad', max_length=200)
    fecha_inicio_planeada = models.DateField('Fecha inicio planeada')
    fecha_fin_planeada = models.DateField('Fecha fin planeada')
    responsable = models.CharField('Responsable', max_length=200)
    recursos = models.TextField('Recursos', blank=True)
    entregable = models.CharField('Entregable', max_length=200, blank=True)
    orden = models.PositiveSmallIntegerField('Orden', default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Item de Cronograma'
        verbose_name_plural = 'Items de Cronograma'
        ordering = ['orden', 'fecha_inicio_planeada']

    def __str__(self):
        return self.actividad


# ============================================================================
# ETAPA 3: IMPLEMENTACIÓN
# ============================================================================

class Etapa3Implementacion(models.Model):
    """Etapa 3: Implementación."""

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_PROCESO = 'EN_PROCESO', 'En proceso'
        COMPLETADO = 'COMPLETADO', 'Completado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proveedor_proyecto = models.OneToOneField(
        ProveedorProyecto,
        on_delete=models.CASCADE,
        related_name='etapa3',
        verbose_name='Proveedor en Proyecto'
    )
    estado = models.CharField(
        'Estado',
        max_length=15,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )
    fecha_inicio = models.DateTimeField('Fecha de inicio', null=True, blank=True)
    fecha_fin = models.DateTimeField('Fecha de finalización', null=True, blank=True)
    porcentaje_avance = models.DecimalField(
        'Porcentaje de avance',
        max_digits=5,
        decimal_places=2,
        default=0
    )
    horas_acompanamiento = models.DecimalField(
        'Horas de acompañamiento',
        max_digits=6,
        decimal_places=2,
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Etapa 3 - Implementación'
        verbose_name_plural = 'Etapas 3 - Implementaciones'

    def __str__(self):
        return f"E3: {self.proveedor_proyecto}"

    def calcular_avance(self):
        """Calcular avance basado en tareas completadas."""
        tareas = self.tareas.all()
        if not tareas.exists():
            return 0
        total = tareas.count()
        completadas = tareas.filter(estado='COMPLETADA').count()
        self.porcentaje_avance = (completadas / total) * 100
        self.save(update_fields=['porcentaje_avance'])
        return self.porcentaje_avance

    def completar(self):
        if self.porcentaje_avance >= 100:
            self.estado = self.Estado.COMPLETADO
            self.fecha_fin = timezone.now()
            self.save()
            # Crear Etapa 4
            Etapa4Monitoreo.objects.get_or_create(proveedor_proyecto=self.proveedor_proyecto)
            # Avanzar etapa
            self.proveedor_proyecto.etapa_actual = 4
            self.proveedor_proyecto.save()


class TareaImplementacion(models.Model):
    """Tareas de implementación (Kanban)."""

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_PROGRESO = 'EN_PROGRESO', 'En progreso'
        COMPLETADA = 'COMPLETADA', 'Completada'
        BLOQUEADA = 'BLOQUEADA', 'Bloqueada'

    class Prioridad(models.TextChoices):
        ALTA = 'ALTA', 'Alta'
        MEDIA = 'MEDIA', 'Media'
        BAJA = 'BAJA', 'Baja'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etapa3 = models.ForeignKey(
        Etapa3Implementacion,
        on_delete=models.CASCADE,
        related_name='tareas',
        verbose_name='Etapa 3'
    )
    cronograma_item = models.ForeignKey(
        CronogramaImplementacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tareas',
        verbose_name='Item de cronograma'
    )
    titulo = models.CharField('Título', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)
    estado = models.CharField(
        'Estado',
        max_length=15,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )
    prioridad = models.CharField(
        'Prioridad',
        max_length=10,
        choices=Prioridad.choices,
        default=Prioridad.MEDIA
    )
    fecha_inicio_planeada = models.DateField('Fecha inicio planeada', null=True, blank=True)
    fecha_fin_planeada = models.DateField('Fecha fin planeada', null=True, blank=True)
    fecha_inicio_real = models.DateField('Fecha inicio real', null=True, blank=True)
    fecha_fin_real = models.DateField('Fecha fin real', null=True, blank=True)
    responsable = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tareas_asignadas',
        verbose_name='Responsable'
    )
    porcentaje_avance = models.PositiveSmallIntegerField('% Avance', default=0)
    orden = models.PositiveSmallIntegerField('Orden', default=1)
    notas = models.TextField('Notas', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tarea de Implementación'
        verbose_name_plural = 'Tareas de Implementación'
        ordering = ['orden', '-prioridad', 'fecha_fin_planeada']

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalcular avance de etapa
        self.etapa3.calcular_avance()


class EvidenciaImplementacion(models.Model):
    """Evidencias de las tareas implementadas."""

    class TipoEvidencia(models.TextChoices):
        DOCUMENTO = 'DOCUMENTO', 'Documento'
        IMAGEN = 'IMAGEN', 'Imagen'
        VIDEO = 'VIDEO', 'Video'
        OTRO = 'OTRO', 'Otro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tarea = models.ForeignKey(
        TareaImplementacion,
        on_delete=models.CASCADE,
        related_name='evidencias',
        verbose_name='Tarea'
    )
    tipo = models.CharField('Tipo', max_length=15, choices=TipoEvidencia.choices)
    nombre = models.CharField('Nombre', max_length=200)
    archivo = models.FileField('Archivo', upload_to='etapas/evidencias/')
    descripcion = models.TextField('Descripción', blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, verbose_name='Subido por'
    )

    class Meta:
        verbose_name = 'Evidencia'
        verbose_name_plural = 'Evidencias'

    def __str__(self):
        return self.nombre


class SesionAcompanamiento(models.Model):
    """Sesiones de acompañamiento con el consultor."""

    class Modalidad(models.TextChoices):
        PRESENCIAL = 'PRESENCIAL', 'Presencial'
        VIRTUAL = 'VIRTUAL', 'Virtual'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etapa3 = models.ForeignKey(
        Etapa3Implementacion,
        on_delete=models.CASCADE,
        related_name='sesiones',
        verbose_name='Etapa 3'
    )
    fecha = models.DateTimeField('Fecha y hora')
    duracion_horas = models.DecimalField('Duración (horas)', max_digits=4, decimal_places=2)
    modalidad = models.CharField(
        'Modalidad',
        max_length=15,
        choices=Modalidad.choices,
        default=Modalidad.VIRTUAL
    )
    temas_tratados = models.TextField('Temas tratados')
    compromisos = models.TextField('Compromisos', blank=True)
    participantes = models.TextField('Participantes', blank=True)
    consultor = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sesiones_realizadas',
        verbose_name='Consultor'
    )
    archivo_acta = models.FileField('Acta', upload_to='etapas/actas/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Sesión de Acompañamiento'
        verbose_name_plural = 'Sesiones de Acompañamiento'
        ordering = ['-fecha']

    def __str__(self):
        return f"Sesión {self.fecha.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Actualizar horas de acompañamiento
        total = self.etapa3.sesiones.aggregate(
            total=models.Sum('duracion_horas')
        )['total'] or 0
        self.etapa3.horas_acompanamiento = total
        self.etapa3.save(update_fields=['horas_acompanamiento'])


# ============================================================================
# ETAPA 4: MONITOREO Y EVALUACIÓN
# ============================================================================

class Etapa4Monitoreo(models.Model):
    """Etapa 4: Monitoreo y Evaluación."""

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_PROCESO = 'EN_PROCESO', 'En proceso'
        COMPLETADO = 'COMPLETADO', 'Completado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proveedor_proyecto = models.OneToOneField(
        ProveedorProyecto,
        on_delete=models.CASCADE,
        related_name='etapa4',
        verbose_name='Proveedor en Proyecto'
    )
    estado = models.CharField(
        'Estado',
        max_length=15,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )
    fecha_inicio = models.DateTimeField('Fecha de inicio', null=True, blank=True)
    fecha_fin = models.DateTimeField('Fecha de finalización', null=True, blank=True)
    informe_final_generado = models.BooleanField('Informe final generado', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Etapa 4 - Monitoreo'
        verbose_name_plural = 'Etapas 4 - Monitoreos'

    def __str__(self):
        return f"E4: {self.proveedor_proyecto}"

    def completar(self):
        self.estado = self.Estado.COMPLETADO
        self.fecha_fin = timezone.now()
        self.save()
        # Completar participación del proveedor
        self.proveedor_proyecto.estado = 'COMPLETADO'
        self.proveedor_proyecto.fecha_fin_real = timezone.now().date()
        self.proveedor_proyecto.porcentaje_avance = 100
        self.proveedor_proyecto.save()


class IndicadorKPI(models.Model):
    """Indicadores de desempeño (KPIs)."""

    class Tendencia(models.TextChoices):
        MEJORANDO = 'MEJORANDO', 'Mejorando'
        ESTABLE = 'ESTABLE', 'Estable'
        EMPEORANDO = 'EMPEORANDO', 'Empeorando'

    class FrecuenciaMedicion(models.TextChoices):
        SEMANAL = 'SEMANAL', 'Semanal'
        QUINCENAL = 'QUINCENAL', 'Quincenal'
        MENSUAL = 'MENSUAL', 'Mensual'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etapa4 = models.ForeignKey(
        Etapa4Monitoreo,
        on_delete=models.CASCADE,
        related_name='indicadores',
        verbose_name='Etapa 4'
    )
    objetivo = models.ForeignKey(
        ObjetivoFortalecimiento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='kpis',
        verbose_name='Objetivo asociado'
    )
    nombre = models.CharField('Nombre del indicador', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)
    valor_inicial = models.DecimalField('Valor inicial', max_digits=10, decimal_places=2, default=0)
    valor_actual = models.DecimalField('Valor actual', max_digits=10, decimal_places=2, default=0)
    valor_meta = models.DecimalField('Valor meta', max_digits=10, decimal_places=2, default=0)
    unidad_medida = models.CharField('Unidad de medida', max_length=50, blank=True)
    frecuencia_medicion = models.CharField(
        'Frecuencia de medición',
        max_length=15,
        choices=FrecuenciaMedicion.choices,
        default=FrecuenciaMedicion.SEMANAL
    )
    tendencia = models.CharField(
        'Tendencia',
        max_length=15,
        choices=Tendencia.choices,
        default=Tendencia.ESTABLE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Indicador KPI'
        verbose_name_plural = 'Indicadores KPI'

    def __str__(self):
        return self.nombre

    @property
    def porcentaje_cumplimiento(self):
        if self.valor_meta == 0:
            return 0
        return min((self.valor_actual / self.valor_meta) * 100, 100)

    def actualizar_tendencia(self):
        """Actualiza la tendencia basada en las últimas mediciones."""
        mediciones = self.mediciones.order_by('-fecha_medicion')[:3]
        if len(mediciones) < 2:
            return

        valores = [m.valor for m in mediciones]
        if valores[0] > valores[-1]:
            self.tendencia = self.Tendencia.MEJORANDO
        elif valores[0] < valores[-1]:
            self.tendencia = self.Tendencia.EMPEORANDO
        else:
            self.tendencia = self.Tendencia.ESTABLE
        self.save(update_fields=['tendencia'])


class MedicionKPI(models.Model):
    """Mediciones de los indicadores."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    indicador = models.ForeignKey(
        IndicadorKPI,
        on_delete=models.CASCADE,
        related_name='mediciones',
        verbose_name='Indicador'
    )
    fecha_medicion = models.DateField('Fecha de medición')
    valor = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    observaciones = models.TextField('Observaciones', blank=True)
    registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Registrado por'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Medición de KPI'
        verbose_name_plural = 'Mediciones de KPI'
        ordering = ['-fecha_medicion']

    def __str__(self):
        return f"{self.indicador.nombre}: {self.valor} ({self.fecha_medicion})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Actualizar valor actual del indicador
        self.indicador.valor_actual = self.valor
        self.indicador.save(update_fields=['valor_actual'])
        self.indicador.actualizar_tendencia()


class ReporteSemanal(models.Model):
    """Reportes semanales de avance."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etapa4 = models.ForeignKey(
        Etapa4Monitoreo,
        on_delete=models.CASCADE,
        related_name='reportes_semanales',
        verbose_name='Etapa 4'
    )
    semana_numero = models.PositiveSmallIntegerField('Número de semana')
    fecha_inicio_semana = models.DateField('Inicio de semana')
    fecha_fin_semana = models.DateField('Fin de semana')
    resumen_avance = models.TextField('Resumen de avance')
    logros = models.TextField('Logros de la semana', blank=True)
    dificultades = models.TextField('Dificultades encontradas', blank=True)
    proximas_acciones = models.TextField('Próximas acciones', blank=True)
    enviado = models.BooleanField('Enviado', default=False)
    fecha_envio = models.DateTimeField('Fecha de envío', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reporte Semanal'
        verbose_name_plural = 'Reportes Semanales'
        ordering = ['-semana_numero']
        unique_together = ['etapa4', 'semana_numero']

    def __str__(self):
        return f"Semana {self.semana_numero}"


class EvaluacionDirectiva(models.Model):
    """Evaluaciones con la dirección del proveedor."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etapa4 = models.ForeignKey(
        Etapa4Monitoreo,
        on_delete=models.CASCADE,
        related_name='evaluaciones',
        verbose_name='Etapa 4'
    )
    fecha = models.DateField('Fecha')
    participantes = models.TextField('Participantes')
    objetivos_cumplidos = models.TextField('Objetivos cumplidos')
    objetivos_pendientes = models.TextField('Objetivos pendientes', blank=True)
    ajustes_requeridos = models.TextField('Ajustes requeridos', blank=True)
    decisiones_tomadas = models.TextField('Decisiones tomadas', blank=True)
    archivo_acta = models.FileField('Acta', upload_to='etapas/evaluaciones/', blank=True, null=True)
    aprobado = models.BooleanField('Aprobado', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Evaluación Directiva'
        verbose_name_plural = 'Evaluaciones Directivas'
        ordering = ['-fecha']

    def __str__(self):
        return f"Evaluación {self.fecha}"


class InformeCierre(models.Model):
    """Informe de cierre del fortalecimiento."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etapa4 = models.OneToOneField(
        Etapa4Monitoreo,
        on_delete=models.CASCADE,
        related_name='informe_cierre',
        verbose_name='Etapa 4'
    )
    fecha_generacion = models.DateTimeField('Fecha de generación', auto_now_add=True)
    resumen_ejecutivo = models.TextField('Resumen ejecutivo')
    objetivos_logrados = models.TextField('Objetivos logrados')
    mejoras_implementadas = models.TextField('Mejoras implementadas')
    resultados_kpis = models.JSONField('Resultados de KPIs', default=dict)
    lecciones_aprendidas = models.TextField('Lecciones aprendidas', blank=True)
    recomendaciones = models.TextField('Recomendaciones', blank=True)
    archivo_pdf = models.FileField('PDF del informe', upload_to='etapas/informes/', blank=True, null=True)
    firmado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='informes_firmados',
        verbose_name='Firmado por'
    )
    fecha_firma = models.DateTimeField('Fecha de firma', null=True, blank=True)

    class Meta:
        verbose_name = 'Informe de Cierre'
        verbose_name_plural = 'Informes de Cierre'

    def __str__(self):
        return f"Informe cierre: {self.etapa4.proveedor_proyecto}"
