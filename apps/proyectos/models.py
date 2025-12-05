import uuid
from django.db import models
from django.utils import timezone
from apps.core.models import AuditoriaModel, Usuario
from apps.empresas.models import EmpresaAncla
from apps.proveedores.models import Proveedor


class Proyecto(AuditoriaModel):
    """Modelo para proyectos/ciclos de fortalecimiento."""

    class EstadoProyecto(models.TextChoices):
        PLANEACION = 'PLANEACION', 'En Planeación'
        EN_CURSO = 'EN_CURSO', 'En Curso'
        FINALIZADO = 'FINALIZADO', 'Finalizado'
        CANCELADO = 'CANCELADO', 'Cancelado'
        SUSPENDIDO = 'SUSPENDIDO', 'Suspendido'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField('Código', max_length=20, unique=True, editable=False)
    nombre = models.CharField('Nombre del proyecto', max_length=200)
    empresa_ancla = models.ForeignKey(
        EmpresaAncla,
        on_delete=models.PROTECT,
        related_name='proyectos',
        verbose_name='Empresa Ancla'
    )
    descripcion = models.TextField('Descripción', blank=True)

    # Fechas
    fecha_inicio = models.DateField('Fecha de inicio')
    fecha_fin_planeada = models.DateField('Fecha fin planeada')
    fecha_fin_real = models.DateField('Fecha fin real', null=True, blank=True)

    # Estado
    estado = models.CharField(
        'Estado',
        max_length=15,
        choices=EstadoProyecto.choices,
        default=EstadoProyecto.PLANEACION
    )

    # Equipo
    director_proyecto = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='proyectos_dirigidos',
        verbose_name='Director del proyecto'
    )

    # Financiero
    presupuesto = models.DecimalField(
        'Presupuesto (COP)',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    costo_por_proveedor = models.DecimalField(
        'Costo por proveedor (COP)',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Configuración
    numero_proveedores_planeado = models.PositiveIntegerField(
        'Número de proveedores planeado',
        default=40
    )
    duracion_meses = models.PositiveIntegerField('Duración (meses)', default=3)
    horas_por_proveedor = models.PositiveIntegerField('Horas por proveedor', default=50)

    # Notas
    objetivos = models.TextField('Objetivos del proyecto', blank=True)
    alcance = models.TextField('Alcance', blank=True)
    notas = models.TextField('Notas internas', blank=True)

    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        ordering = ['-fecha_inicio', 'nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def save(self, *args, **kwargs):
        if not self.codigo:
            # Generar código único
            year = timezone.now().year
            count = Proyecto.objects.filter(
                created_at__year=year
            ).count() + 1
            self.codigo = f"PRY-{year}-{count:04d}"
        super().save(*args, **kwargs)

    @property
    def proveedores_count(self):
        """Número de proveedores asignados."""
        return self.proveedores.count()

    @property
    def avance_promedio(self):
        """Avance promedio de todos los proveedores."""
        from django.db.models import Avg
        promedio = self.proveedores.aggregate(Avg('porcentaje_avance'))
        return promedio['porcentaje_avance__avg'] or 0

    @property
    def dias_restantes(self):
        """Días restantes hasta fecha fin planeada."""
        if self.fecha_fin_planeada:
            delta = self.fecha_fin_planeada - timezone.now().date()
            return delta.days
        return None

    @property
    def esta_atrasado(self):
        """Indica si el proyecto está atrasado."""
        if self.dias_restantes is not None and self.estado == self.EstadoProyecto.EN_CURSO:
            return self.dias_restantes < 0
        return False


class ProveedorProyecto(AuditoriaModel):
    """Relación entre proveedores y proyectos (participación en fortalecimiento)."""

    class EstadoParticipacion(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente de iniciar'
        EN_PROCESO = 'EN_PROCESO', 'En proceso'
        COMPLETADO = 'COMPLETADO', 'Completado'
        SUSPENDIDO = 'SUSPENDIDO', 'Suspendido'
        RETIRADO = 'RETIRADO', 'Retirado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name='participaciones',
        verbose_name='Proveedor'
    )
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='proveedores',
        verbose_name='Proyecto'
    )
    consultor_asignado = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='proveedores_asignados',
        verbose_name='Consultor asignado'
    )

    # Etapa y estado
    etapa_actual = models.PositiveSmallIntegerField(
        'Etapa actual',
        default=1,
        choices=[
            (1, 'Etapa 1: Diagnóstico'),
            (2, 'Etapa 2: Plan'),
            (3, 'Etapa 3: Implementación'),
            (4, 'Etapa 4: Monitoreo'),
        ]
    )
    estado = models.CharField(
        'Estado',
        max_length=15,
        choices=EstadoParticipacion.choices,
        default=EstadoParticipacion.PENDIENTE
    )

    # Fechas
    fecha_inicio = models.DateField('Fecha de inicio', null=True, blank=True)
    fecha_fin_planeada = models.DateField('Fecha fin planeada', null=True, blank=True)
    fecha_fin_real = models.DateField('Fecha fin real', null=True, blank=True)

    # Seguimiento
    porcentaje_avance = models.DecimalField(
        'Porcentaje de avance',
        max_digits=5,
        decimal_places=2,
        default=0
    )
    horas_consumidas = models.DecimalField(
        'Horas consumidas',
        max_digits=6,
        decimal_places=2,
        default=0
    )
    horas_planeadas = models.DecimalField(
        'Horas planeadas',
        max_digits=6,
        decimal_places=2,
        default=50
    )

    # Notas
    notas = models.TextField('Notas', blank=True)
    motivo_suspension = models.TextField('Motivo de suspensión/retiro', blank=True)

    class Meta:
        verbose_name = 'Participación de Proveedor'
        verbose_name_plural = 'Participaciones de Proveedores'
        unique_together = ['proveedor', 'proyecto']
        ordering = ['proyecto', 'proveedor']

    def __str__(self):
        return f"{self.proveedor} en {self.proyecto}"

    @property
    def etapa_nombre(self):
        """Nombre de la etapa actual."""
        nombres = {
            1: 'Diagnóstico',
            2: 'Plan',
            3: 'Implementación',
            4: 'Monitoreo'
        }
        return nombres.get(self.etapa_actual, 'Desconocida')

    @property
    def puede_avanzar_etapa(self):
        """Verifica si puede avanzar a la siguiente etapa."""
        if self.etapa_actual >= 4:
            return False

        # Verificar que la etapa actual esté completada
        if self.etapa_actual == 1:
            return hasattr(self, 'etapa1') and self.etapa1.estado == 'COMPLETADO'
        elif self.etapa_actual == 2:
            return hasattr(self, 'etapa2') and self.etapa2.estado == 'APROBADO'
        elif self.etapa_actual == 3:
            return hasattr(self, 'etapa3') and self.etapa3.estado == 'COMPLETADO'

        return False

    def avanzar_etapa(self):
        """Avanza a la siguiente etapa si es posible."""
        if self.puede_avanzar_etapa:
            self.etapa_actual += 1
            self.save()
            return True
        return False

    def calcular_avance(self):
        """Calcula el porcentaje de avance basado en las etapas completadas."""
        avance = 0

        # Cada etapa vale 25%
        if hasattr(self, 'etapa1') and self.etapa1.estado == 'COMPLETADO':
            avance += 25
        if hasattr(self, 'etapa2') and self.etapa2.estado == 'APROBADO':
            avance += 25
        if hasattr(self, 'etapa3'):
            # Etapa 3 se calcula por porcentaje de tareas completadas
            avance += (self.etapa3.porcentaje_avance * 0.25)
        if hasattr(self, 'etapa4') and self.etapa4.estado == 'COMPLETADO':
            avance += 25

        self.porcentaje_avance = avance
        self.save(update_fields=['porcentaje_avance'])
        return avance


class DocumentoProyecto(models.Model):
    """Documentos generales del proyecto."""

    class TipoDocumento(models.TextChoices):
        PROPUESTA = 'PROPUESTA', 'Propuesta'
        CONTRATO = 'CONTRATO', 'Contrato'
        INFORME = 'INFORME', 'Informe'
        PRESENTACION = 'PRESENTACION', 'Presentación'
        ACTA = 'ACTA', 'Acta'
        OTRO = 'OTRO', 'Otro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name='Proyecto'
    )
    tipo = models.CharField(
        'Tipo de documento',
        max_length=15,
        choices=TipoDocumento.choices
    )
    nombre = models.CharField('Nombre', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)
    archivo = models.FileField('Archivo', upload_to='proyectos/documentos/')
    version = models.CharField('Versión', max_length=20, default='1.0')
    uploaded_at = models.DateTimeField('Subido', auto_now_add=True)
    uploaded_by = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Subido por'
    )

    class Meta:
        verbose_name = 'Documento del Proyecto'
        verbose_name_plural = 'Documentos del Proyecto'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.proyecto.codigo} - {self.nombre}"
