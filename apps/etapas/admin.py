from django.contrib import admin
from .models import (
    Etapa1Diagnostico, VozCliente, DiagnosticoCompetitividad, ObjetivoFortalecimiento, DocumentoEtapa1,
    Etapa2Plan, HallazgoProblema, AccionMejora, CronogramaImplementacion,
    Etapa3Implementacion, TareaImplementacion, EvidenciaImplementacion, SesionAcompanamiento,
    Etapa4Monitoreo, IndicadorKPI, MedicionKPI, ReporteSemanal, EvaluacionDirectiva, InformeCierre
)


# ============================================================================
# ETAPA 1
# ============================================================================

class VozClienteInline(admin.TabularInline):
    model = VozCliente
    extra = 0


class DiagnosticoInline(admin.TabularInline):
    model = DiagnosticoCompetitividad
    extra = 0


class ObjetivoInline(admin.TabularInline):
    model = ObjetivoFortalecimiento
    extra = 0


class DocumentoEtapa1Inline(admin.TabularInline):
    model = DocumentoEtapa1
    extra = 0
    readonly_fields = ['uploaded_at', 'uploaded_by']


@admin.register(Etapa1Diagnostico)
class Etapa1DiagnosticoAdmin(admin.ModelAdmin):
    list_display = ('proveedor_proyecto', 'estado', 'fecha_inicio', 'fecha_fin')
    list_filter = ('estado', 'fecha_inicio')
    search_fields = ('proveedor_proyecto__proveedor__razon_social',)
    inlines = [VozClienteInline, DiagnosticoInline, ObjetivoInline, DocumentoEtapa1Inline]


# ============================================================================
# ETAPA 2
# ============================================================================

class HallazgoInline(admin.TabularInline):
    model = HallazgoProblema
    extra = 0


class CronogramaInline(admin.TabularInline):
    model = CronogramaImplementacion
    extra = 0


@admin.register(Etapa2Plan)
class Etapa2PlanAdmin(admin.ModelAdmin):
    list_display = ('proveedor_proyecto', 'estado', 'fecha_inicio', 'aprobado_por', 'fecha_aprobacion')
    list_filter = ('estado', 'fecha_aprobacion')
    search_fields = ('proveedor_proyecto__proveedor__razon_social',)
    inlines = [HallazgoInline, CronogramaInline]


@admin.register(HallazgoProblema)
class HallazgoProblemaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'etapa2', 'hallazgo', 'prioridad')
    list_filter = ('prioridad',)


@admin.register(AccionMejora)
class AccionMejoraAdmin(admin.ModelAdmin):
    list_display = ('hallazgo', 'descripcion', 'tipo_accion', 'impacto_esperado', 'esfuerzo_requerido', 'seleccionada')
    list_filter = ('tipo_accion', 'seleccionada')


# ============================================================================
# ETAPA 3
# ============================================================================

class TareaInline(admin.TabularInline):
    model = TareaImplementacion
    extra = 0


class SesionInline(admin.TabularInline):
    model = SesionAcompanamiento
    extra = 0


@admin.register(Etapa3Implementacion)
class Etapa3ImplementacionAdmin(admin.ModelAdmin):
    list_display = ('proveedor_proyecto', 'estado', 'porcentaje_avance', 'horas_acompanamiento')
    list_filter = ('estado',)
    search_fields = ('proveedor_proyecto__proveedor__razon_social',)
    inlines = [TareaInline, SesionInline]


@admin.register(TareaImplementacion)
class TareaImplementacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'etapa3', 'estado', 'prioridad', 'fecha_fin_planeada', 'porcentaje_avance')
    list_filter = ('estado', 'prioridad')
    search_fields = ('titulo',)


# ============================================================================
# ETAPA 4
# ============================================================================

class IndicadorInline(admin.TabularInline):
    model = IndicadorKPI
    extra = 0


class ReporteInline(admin.TabularInline):
    model = ReporteSemanal
    extra = 0


class EvaluacionInline(admin.TabularInline):
    model = EvaluacionDirectiva
    extra = 0


@admin.register(Etapa4Monitoreo)
class Etapa4MonitoreoAdmin(admin.ModelAdmin):
    list_display = ('proveedor_proyecto', 'estado', 'fecha_inicio', 'informe_final_generado')
    list_filter = ('estado', 'informe_final_generado')
    search_fields = ('proveedor_proyecto__proveedor__razon_social',)
    inlines = [IndicadorInline, ReporteInline, EvaluacionInline]


@admin.register(IndicadorKPI)
class IndicadorKPIAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'etapa4', 'valor_inicial', 'valor_actual', 'valor_meta', 'tendencia')
    list_filter = ('tendencia', 'frecuencia_medicion')


@admin.register(InformeCierre)
class InformeCierreAdmin(admin.ModelAdmin):
    list_display = ('etapa4', 'fecha_generacion', 'firmado_por', 'fecha_firma')
    readonly_fields = ['fecha_generacion']
