import uuid
from django.db import models
from apps.core.models import Usuario
from apps.empresas.models import EmpresaAncla


class ReporteGenerado(models.Model):
    """Reportes generados en el sistema."""

    class TipoReporte(models.TextChoices):
        AVANCE_PROVEEDOR = 'AVANCE_PROVEEDOR', 'Avance por Proveedor'
        CONSOLIDADO_PROYECTO = 'CONSOLIDADO_PROYECTO', 'Consolidado de Proyecto'
        EJECUTIVO = 'EJECUTIVO', 'Informe Ejecutivo'
        COMPARATIVO = 'COMPARATIVO', 'Comparativo'
        KPIS = 'KPIS', 'Reporte de KPIs'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField('Tipo', max_length=25, choices=TipoReporte.choices)
    nombre = models.CharField('Nombre', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)
    parametros = models.JSONField('Parámetros', default=dict)
    archivo = models.FileField('Archivo', upload_to='reportes/')
    formato = models.CharField('Formato', max_length=10, default='PDF')
    generado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, related_name='reportes_generados'
    )
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reporte Generado'
        verbose_name_plural = 'Reportes Generados'
        ordering = ['-fecha_generacion']

    def __str__(self):
        return f"{self.nombre} - {self.fecha_generacion.strftime('%Y-%m-%d')}"


class PlantillaReporte(models.Model):
    """Plantillas para generación de reportes."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField('Nombre', max_length=200)
    tipo_reporte = models.CharField('Tipo', max_length=25, choices=ReporteGenerado.TipoReporte.choices)
    descripcion = models.TextField('Descripción', blank=True)
    archivo_plantilla = models.FileField('Plantilla', upload_to='reportes/plantillas/', blank=True, null=True)
    configuracion = models.JSONField('Configuración', default=dict)
    is_active = models.BooleanField('Activa', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Plantilla de Reporte'
        verbose_name_plural = 'Plantillas de Reportes'

    def __str__(self):
        return self.nombre


class ConfiguracionReporteAutomatico(models.Model):
    """Configuración para reportes automáticos."""

    class Frecuencia(models.TextChoices):
        DIARIO = 'DIARIO', 'Diario'
        SEMANAL = 'SEMANAL', 'Semanal'
        QUINCENAL = 'QUINCENAL', 'Quincenal'
        MENSUAL = 'MENSUAL', 'Mensual'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empresa_ancla = models.ForeignKey(
        EmpresaAncla, on_delete=models.CASCADE, related_name='configuraciones_reporte'
    )
    tipo_reporte = models.CharField('Tipo', max_length=25, choices=ReporteGenerado.TipoReporte.choices)
    frecuencia = models.CharField('Frecuencia', max_length=15, choices=Frecuencia.choices)
    destinatarios = models.JSONField('Destinatarios', default=list)
    hora_envio = models.TimeField('Hora de envío', default='08:00')
    is_active = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Configuración de Reporte Automático'
        verbose_name_plural = 'Configuraciones de Reportes Automáticos'

    def __str__(self):
        return f"{self.empresa_ancla} - {self.get_tipo_reporte_display()}"
